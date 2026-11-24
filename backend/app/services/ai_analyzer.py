"""
AI-powered analysis using Google Gemini or OpenAI (plain REST calls via httpx).

`analyze_with_ai` returns a validated AnalysisResult, or raises AIAnalysisError so the
caller can fall back to the offline analyzer.
"""
import json
import logging
import re

import httpx
from pydantic import ValidationError

from ..config import settings
from ..schemas import AnalysisResult

log = logging.getLogger("resumeiq.ai")

# Keep prompts within a sensible token budget
MAX_RESUME_CHARS = 15000
MAX_JD_CHARS = 6000

SYSTEM_PROMPT = "You are an expert technical recruiter and ATS (Applicant Tracking System) specialist."

PROMPT_TEMPLATE = """Analyze the RESUME against the JOB DESCRIPTION{role_hint}.

Return ONLY a JSON object (no markdown, no commentary) in exactly this format:
{{
  "candidate": {{ "name": "", "email": "", "phone": "", "education": [], "experience": [], "projects": [], "certifications": [] }},
  "match_score": 0,
  "ats_score": 0,
  "section_scores": {{ "skills": 0, "experience": 0, "education": 0, "projects": 0, "formatting": 0 }},
  "skills_found": [],
  "missing_skills": [],
  "strengths": [],
  "suggestions": [],
  "summary": ""
}}

Rules:
- All scores are integers from 0 to 100. Be realistic and critical, not generous.
- match_score: how well the candidate fits THIS job description overall.
- ats_score: how well an ATS would parse and rank the resume (keywords, standard headings, contact info, simple layout).
- candidate.education / experience / projects / certifications: arrays of short strings,
  e.g. "B.Tech Computer Science, XYZ University (2021–2025), CGPA 8.4" or "Software Intern, ABC Corp (Jun–Aug 2024)". Use [] if absent.
- skills_found: skills from the job description that ARE present in the resume (short names like "React", "SQL").
- missing_skills: important skills/keywords from the job description that are NOT in the resume.
- strengths: 3–5 short points.
- suggestions: 6–10 specific, actionable improvements. Include:
  * at least 2 weak bullet points from the resume rewritten with strong action verbs and metrics,
    formatted as: Rewrite "original text" → "improved text"
  * which missing keywords to add and where,
  * any formatting / structure issues.
- summary: 2–3 sentence overall assessment.
- Never invent information that is not in the resume for the candidate fields.

JOB DESCRIPTION:
\"\"\"{jd}\"\"\"

RESUME:
\"\"\"{resume}\"\"\"
"""


class AIAnalysisError(Exception):
    """Raised when the AI provider fails or returns unusable output."""


def build_prompt(resume_text: str, job_description: str, job_role: str = "") -> str:
    return PROMPT_TEMPLATE.format(
        role_hint=f" for the role of {job_role}" if job_role else "",
        jd=job_description[:MAX_JD_CHARS],
        resume=resume_text[:MAX_RESUME_CHARS],
    )


def parse_json_response(raw: str) -> dict:
    """Extract a JSON object from the model output, tolerating ```json fences or extra text."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    raise AIAnalysisError("AI response was not valid JSON")


async def _call_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
        r = await client.post(url, json=body, headers={"x-goog-api-key": settings.GEMINI_API_KEY})
    if r.status_code != 200:
        raise AIAnalysisError(f"Gemini API error {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError):
        raise AIAnalysisError(f"Unexpected Gemini response: {str(data)[:300]}")


async def _call_openai(prompt: str) -> str:
    body = {
        "model": settings.OPENAI_MODEL,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", json=body,
                              headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"})
    if r.status_code != 200:
        raise AIAnalysisError(f"OpenAI API error {r.status_code}: {r.text[:300]}")
    try:
        return r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise AIAnalysisError("Unexpected OpenAI response format")


async def analyze_with_ai(resume_text: str, job_description: str, job_role: str = ""):
    """Run the analysis with the configured provider. Returns (AnalysisResult, provider_name)."""
    provider = settings.active_provider
    if provider == "none":
        raise AIAnalysisError("No AI API key configured")

    prompt = build_prompt(resume_text, job_description, job_role)
    try:
        raw = await (_call_gemini(prompt) if provider == "gemini" else _call_openai(prompt))
    except httpx.HTTPError as exc:
        raise AIAnalysisError(f"Network error calling {provider}: {exc}") from exc

    data = parse_json_response(raw)
    if not isinstance(data, dict):
        raise AIAnalysisError("AI response JSON was not an object")
    try:
        result = AnalysisResult.model_validate(data)
    except ValidationError as exc:
        raise AIAnalysisError(f"AI JSON failed validation: {exc}") from exc

    # Sanity check: a response with no scores and no skills is almost certainly broken
    if result.match_score == 0 and not result.skills_found and not result.suggestions:
        raise AIAnalysisError("AI returned an empty analysis")
    return result, provider
