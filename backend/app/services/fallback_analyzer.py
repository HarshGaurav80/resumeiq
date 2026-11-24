"""
Offline analyzer – used when no AI key is configured or the AI call fails.

Pipeline:
1. Rule-based extraction of candidate details (regex + section headings).
2. Keyword matching of resume & job description against the built-in skills list.
3. TF-IDF + cosine similarity between resume text and job description.
4. Heuristic section scores, ATS checks and actionable suggestions.

It returns the same JSON structure as the AI so the frontend doesn't care which was used.
"""
import math
import re
from typing import Dict, List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..schemas import AnalysisResult
from .skills_db import (ACTION_VERBS, ALIASES, CASE_SENSITIVE_SKILLS, ROLE_SKILLS, SKILLS,
                        WEAK_PHRASES)

# --------------------------------------------------------------------------------------
# Skill matching
# --------------------------------------------------------------------------------------

# Characters that may NOT touch a skill term on either side (so "Java" doesn't match "JavaScript")
_LEFT = r"(?<![A-Za-z0-9+#.&])"
_RIGHT = r"(?![A-Za-z0-9+#&])"


def _compile_skill_patterns() -> List[Tuple[re.Pattern, str]]:
    patterns = []
    terms = [(s, s) for s in SKILLS] + [(alias, canon) for alias, canon in ALIASES.items()]
    for term, canonical in terms:
        flags = 0 if term in CASE_SENSITIVE_SKILLS else re.IGNORECASE
        # allow flexible whitespace/hyphen inside multi-word terms ("problem-solving")
        body = r"[\s\-]+".join(re.escape(part) for part in term.split())
        patterns.append((re.compile(_LEFT + body + _RIGHT, flags), canonical))
    return patterns


_SKILL_PATTERNS = _compile_skill_patterns()


def extract_skills(text: str) -> List[str]:
    """Return canonical skill names found in `text`, ordered by first appearance."""
    found: Dict[str, int] = {}
    for pattern, canonical in _SKILL_PATTERNS:
        m = pattern.search(text)
        if m and (canonical not in found or m.start() < found[canonical]):
            found[canonical] = m.start()
    return sorted(found, key=found.get)


# --------------------------------------------------------------------------------------
# Candidate detail extraction
# --------------------------------------------------------------------------------------

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{8,16}\d")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
BULLET_RE = re.compile(r"^\s*[•\-*▪◦●■–>]\s*")

# Section heading keywords -> section key
SECTION_HEADINGS = {
    "summary": ["summary", "professional summary", "objective", "career objective", "profile",
                "about me", "about", "professional profile"],
    "education": ["education", "academic background", "academics", "educational qualifications",
                  "qualifications", "academic qualifications", "education & training"],
    "experience": ["experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "internships", "internship",
                   "internship experience", "relevant experience"],
    "projects": ["projects", "academic projects", "personal projects", "key projects",
                 "project experience", "selected projects"],
    "certifications": ["certifications", "certificates", "certification", "licenses & certifications",
                       "courses", "certifications & courses", "courses & certifications", "training"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "skills & tools",
               "technical proficiency", "tools & technologies", "soft skills"],
    "other": ["achievements", "awards", "honors", "hobbies", "interests", "languages",
              "extracurricular activities", "extra-curricular activities", "activities",
              "references", "declaration", "publications", "volunteering", "positions of responsibility",
              "leadership", "personal details", "contact", "links"],
}
_HEADING_LOOKUP = {h: key for key, hs in SECTION_HEADINGS.items() for h in hs}


def _heading_key(line: str) -> Optional[str]:
    norm = re.sub(r"[^a-z&\- ]", "", line.lower()).strip()
    norm = re.sub(r"\s+", " ", norm)
    if not norm or len(norm) > 40:
        return None
    return _HEADING_LOOKUP.get(norm)


def split_sections(text: str) -> Dict[str, List[str]]:
    """Split resume lines into sections keyed by heading type ('header' = before first heading)."""
    sections: Dict[str, List[str]] = {"header": []}
    current = "header"
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        key = _heading_key(line)
        if key:
            current = key
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _section_items(lines: List[str], limit: int = 10) -> List[str]:
    """Turn section lines into items, joining wrapped lines that continue a previous bullet."""
    items: List[str] = []
    for line in lines:
        is_bullet = bool(BULLET_RE.match(line))
        clean = BULLET_RE.sub("", line).strip()
        if not clean:
            continue
        if items and not is_bullet and (clean[0].islower() or clean[0] in "(&"):
            items[-1] += " " + clean  # wrapped continuation line
        else:
            items.append(clean)
    return [i[:220] for i in items[:limit]]


def _guess_name(header_lines: List[str], all_lines: List[str]) -> str:
    for line in (header_lines or all_lines)[:6]:
        candidate = re.split(r"[|,•]", line)[0].strip()
        words = candidate.split()
        if (2 <= len(words) <= 4 and not any(ch.isdigit() for ch in candidate)
                and "@" not in candidate and not _heading_key(candidate)
                and all(re.fullmatch(r"[A-Za-z.'\-]+", w) for w in words)):
            return candidate.title() if candidate.isupper() else candidate
    return ""


def extract_candidate(text: str) -> Tuple[dict, Dict[str, List[str]]]:
    sections = split_sections(text)
    all_lines = [l.strip() for l in text.split("\n") if l.strip()]

    email = EMAIL_RE.search(text)
    phone = ""
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if 10 <= len(digits) <= 13 and not YEAR_RE.fullmatch(m.group().strip()):
            phone = m.group().strip()
            break

    candidate = {
        "name": _guess_name(sections.get("header", []), all_lines),
        "email": email.group() if email else "",
        "phone": phone,
        "education": _section_items(sections.get("education", []), 6),
        "experience": _section_items(sections.get("experience", []), 10),
        "projects": _section_items(sections.get("projects", []), 10),
        "certifications": _section_items(sections.get("certifications", []), 8),
    }
    return candidate, sections


# --------------------------------------------------------------------------------------
# Scoring helpers
# --------------------------------------------------------------------------------------

def tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Cosine similarity (0–1) of TF-IDF vectors for the resume and the job description."""
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        matrix = vec.fit_transform([resume_text.lower(), jd_text.lower()])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:  # empty vocabulary
        return 0.0


def _bullet_lines(sections: Dict[str, List[str]]) -> List[str]:
    """Achievement lines from experience/projects. If the resume uses bullet markers, only those
    lines count (so job-title / project-title lines aren't judged as bullets)."""
    lines = sections.get("experience", []) + sections.get("projects", [])
    marked = [l for l in lines if BULLET_RE.match(l)]
    lines = marked or lines
    return [BULLET_RE.sub("", l).strip() for l in lines if len(l.split()) >= 4]


# Text after these headings in a job description is "nice to have" and weighted lower
NICE_TO_HAVE_RE = re.compile(r"(nice[\s-]to[\s-]have|good[\s-]to[\s-]have|preferred|bonus|plus points?)\b", re.I)


_ACTION_SET = {v.lower() for v in ACTION_VERBS} | {
    "wrote", "used", "added", "assisted", "maintained", "supported", "conducted", "organized",
    "prepared", "planned", "earned", "won", "handled", "performed", "produced", "contributed",
    "boosted", "cut", "saved", "scaled", "shipped", "owned", "refactored", "visualized", "modeled",
}


def _starts_with_action_verb(line: str) -> bool:
    first = re.sub(r"[^a-z]", "", line.split()[0].lower()) if line.split() else ""
    return first in _ACTION_SET or (first.endswith("ed") and len(first) > 4)


def _is_quantified(line: str) -> bool:
    return bool(re.search(r"\d+\s*(%|\+|x\b|k\b|users|students|clients|hours|ms|seconds|days|lakh|crore)",
                          line, re.I) or re.search(r"[$₹€£]\s?\d", line))


_IRREGULAR_PAST = {"making": "Made", "building": "Built", "writing": "Wrote", "leading": "Led",
                   "running": "Ran", "doing": "Did", "setting": "Set", "getting": "Got", "teaching": "Taught"}


def _gerund_to_past(word: str) -> Optional[str]:
    """'fixing' -> 'Fixed', 'creating' -> 'Created', 'making' -> 'Made'; None if not a gerund."""
    w = word.lower()
    if w in _IRREGULAR_PAST:
        return _IRREGULAR_PAST[w]
    if w.endswith("ing") and len(w) > 5:
        return (w[:-3] + "ed").capitalize()  # creat+ed, manag+ed, plann+ed all work
    return None


def rewrite_weak_bullet(line: str) -> Optional[str]:
    """Rewrite a weak bullet ('Responsible for ...') with a strong action verb, or return None."""
    text = line.strip().rstrip(".")
    for pattern, verb in WEAK_PHRASES:
        m = re.match(pattern, text.lower())
        if not m:
            continue
        rest = text[m.end():]
        # "Worked on fixing bugs" -> "Fixed bugs" rather than "Developed fixing bugs"
        first, _, remainder = rest.partition(" ")
        past = _gerund_to_past(first)
        new = f"{past} {remainder}" if past and remainder else f"{verb}{rest}"
        return f"{new}, resulting in [measurable result – e.g. users served, % improvement or time saved]."
    return None


# --------------------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------------------

def analyze_offline(resume_text: str, job_description: str, job_role: str = "") -> AnalysisResult:
    candidate, sections = extract_candidate(resume_text)
    words = len(resume_text.split())
    lower = resume_text.lower()

    # ---- Skills --------------------------------------------------------------------
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)
    if len(jd_skills) < 5 and job_role in ROLE_SKILLS:
        # Job description is thin -> supplement with the role's core skills
        jd_skills += [s for s in ROLE_SKILLS[job_role] if s not in jd_skills]

    # Skills that only appear in a "Nice to have" part of the JD count half as much
    m = NICE_TO_HAVE_RE.search(job_description)
    core_skills = set(extract_skills(job_description[:m.start()])) if m else set(jd_skills)
    weight = {s: (1.0 if s in core_skills or s not in extract_skills(job_description) else 0.5) for s in jd_skills}

    resume_set = {s.lower() for s in resume_skills}
    if jd_skills:
        skills_found = [s for s in jd_skills if s.lower() in resume_set]
        missing = [s for s in jd_skills if s.lower() not in resume_set]
        # required skills first in the "missing" list
        missing.sort(key=lambda s: -weight[s])
        coverage = sum(weight[s] for s in skills_found) / sum(weight.values()) * 100
    else:
        skills_found, missing = resume_skills, []
        coverage = min(100, len(resume_skills) * 8)

    # ---- TF-IDF similarity ------------------------------------------------------------
    sim = tfidf_similarity(resume_text, job_description)
    sim_score = min(100.0, math.sqrt(sim) * 150)  # typical sims are 0.05–0.4

    # ---- Section scores --------------------------------------------------------------
    bullets = _bullet_lines(sections)
    action_ratio = (sum(_starts_with_action_verb(b) for b in bullets) / len(bullets)) if bullets else 0
    quant_ratio = (sum(_is_quantified(b) for b in bullets) / len(bullets)) if bullets else 0

    exp_score = (35 if sections.get("experience") else 10) \
        + min(len(candidate["experience"]), 6) * 4 \
        + action_ratio * 20 + quant_ratio * 25 + (5 if YEAR_RE.search(" ".join(sections.get("experience", []))) else 0)

    edu_text = " ".join(sections.get("education", [])).lower() or lower
    degree = re.search(r"b\.?\s?tech|b\.?e\b|bachelor|master|m\.?\s?tech|b\.?sc|m\.?sc|mca|bca|ph\.?d|diploma|"
                       r"b\.?com|mba|degree|university|college", edu_text)
    edu_score = (40 if sections.get("education") else 10) + (30 if degree else 0) \
        + (15 if re.search(r"cgpa|gpa|percentage|\d{1,2}(\.\d+)?\s*%|\d\.\d{1,2}\s*/\s*10", edu_text) else 0) \
        + (15 if YEAR_RE.search(edu_text) else 0)

    proj_text = " ".join(sections.get("projects", []))
    proj_score = (30 if sections.get("projects") else 5) + min(len(candidate["projects"]), 4) * 8 \
        + (15 if extract_skills(proj_text) else 0) \
        + (15 if re.search(r"github\.com|gitlab\.com|https?://|live demo|deployed", proj_text, re.I) else 0) \
        + quant_ratio * 10

    has_core = [k for k in ("education", "skills") if sections.get(k)]
    has_exp_or_proj = bool(sections.get("experience") or sections.get("projects"))
    any_bullets = any(BULLET_RE.match(l) for l in resume_text.split("\n"))
    fmt_score = (15 if candidate["email"] else 0) + (15 if candidate["phone"] else 0) \
        + (5 if candidate["name"] else 0) + len(has_core) * 10 + (10 if has_exp_or_proj else 0) \
        + (15 if 250 <= words <= 1000 else 5) + (10 if any_bullets else 0) \
        + (10 if re.search(r"linkedin\.com|github\.com", lower) else 0)

    section_scores = {
        "skills": coverage,
        "experience": exp_score,
        "education": edu_score,
        "projects": proj_score,
        "formatting": fmt_score,
    }
    section_scores = {k: int(round(max(0, min(100, v)))) for k, v in section_scores.items()}

    content_avg = (section_scores["experience"] + section_scores["projects"] + section_scores["education"]) / 3
    match_score = 0.55 * coverage + 0.30 * sim_score + 0.15 * content_avg
    ats_score = 0.45 * section_scores["formatting"] + 0.40 * coverage + 0.15 * sim_score

    # ---- Strengths -------------------------------------------------------------------
    strengths: List[str] = []
    if coverage >= 60:
        strengths.append(f"Strong keyword alignment: {len(skills_found)} of {len(jd_skills)} "
                         f"job-description skills are present.")
    if skills_found:
        strengths.append("Relevant skills highlighted: " + ", ".join(skills_found[:6]) + ".")
    if quant_ratio >= 0.3:
        strengths.append("Achievements are quantified with numbers, which recruiters and ATS reward.")
    if action_ratio >= 0.5:
        strengths.append("Bullet points mostly start with strong action verbs.")
    if section_scores["projects"] >= 70:
        strengths.append("Projects section is detailed and demonstrates hands-on experience.")
    if section_scores["education"] >= 70:
        strengths.append("Education section is complete with degree, institution and dates/grades.")
    if candidate["email"] and candidate["phone"]:
        strengths.append("Contact information is clear and easy for an ATS to parse.")
    if not strengths:
        strengths.append("Resume text is machine-readable, so ATS systems can parse it.")

    # ---- Suggestions -----------------------------------------------------------------
    suggestions: List[str] = []
    if missing:
        suggestions.append("Add these missing job-description keywords (only if you genuinely have them), "
                           "ideally inside experience/project bullet points: " + ", ".join(missing[:10]) + ".")
    rewrites = 0
    for b in bullets:
        new = rewrite_weak_bullet(b)
        if new and rewrites < 4:
            suggestions.append(f"Rewrite weak bullet: \"{b[:120]}\" → \"{new}\"")
            rewrites += 1
    if bullets and action_ratio < 0.6:
        suggestions.append("Start every bullet with a strong action verb such as "
                           + ", ".join(ACTION_VERBS[:8]) + ".")
    if quant_ratio < 0.3:
        suggestions.append("Quantify your impact – add numbers like users served, % performance improved, "
                           "time saved or dataset size (e.g. \"Reduced API latency by 40%\").")
    if not sections.get("summary"):
        suggestions.append(f"Add a 2–3 line professional summary at the top tailored to the "
                           f"{job_role or 'target'} role, mentioning your top 3 matching skills.")
    if not sections.get("skills"):
        suggestions.append("Add a dedicated 'Skills' section with a clear heading so ATS systems can find your skills.")
    if not sections.get("projects"):
        suggestions.append("Add a 'Projects' section with 2–3 projects that use the technologies in the job description.")
    if not sections.get("experience"):
        suggestions.append("Add internships, freelance work or open-source contributions under an 'Experience' heading.")
    if not candidate["email"] or not candidate["phone"]:
        suggestions.append("Make sure your email and phone number are in plain text at the top of the resume.")
    if not re.search(r"linkedin\.com", lower):
        suggestions.append("Add your LinkedIn profile URL to the header.")
    if not re.search(r"github\.com", lower) and job_role not in ("Product Manager", "Business Analyst", "UI/UX Designer"):
        suggestions.append("Add a GitHub link (and links to live project demos) so recruiters can verify your work.")
    if words < 250:
        suggestions.append(f"Your resume is short ({words} words). Expand project and experience details to 400–700 words.")
    elif words > 1000:
        suggestions.append(f"Your resume is long ({words} words). Trim it to 1–2 pages focused on relevant work.")
    suggestions.append("Use a simple single-column layout with standard headings (Summary, Skills, Experience, "
                       "Projects, Education) and avoid tables, images or text boxes that ATS may not read.")

    # ---- Summary ---------------------------------------------------------------------
    level = "a strong" if round(match_score) > 75 else "a moderate" if round(match_score) >= 50 else "a weak"
    summary = (f"The resume is {level} match for this {job_role or 'role'} "
               f"({round(match_score)}/100). It covers {len(jd_skills) - len(missing)} of {len(jd_skills)} key skills"
               + (f"; the most important gaps are {', '.join(missing[:3])}." if missing else ".")
               + " Analysis performed offline using keyword matching and TF-IDF similarity.")

    return AnalysisResult.model_validate({
        "candidate": candidate,
        "match_score": match_score,
        "ats_score": ats_score,
        "section_scores": section_scores,
        "skills_found": skills_found,
        "missing_skills": missing,
        "strengths": strengths,
        "suggestions": suggestions,
        "summary": summary,
    })
