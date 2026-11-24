"""
Pydantic models describing the analysis result.

The AI is asked to return JSON in exactly this shape. `AnalysisResult.model_validate`
is used to validate it; validators coerce/clamp sloppy values (e.g. "85" -> 85,
120 -> 100, a string where a list was expected) so a slightly-off AI response
doesn't break the app.
"""
from typing import Any, List

from pydantic import BaseModel, Field, field_validator


def _clamp_score(v: Any) -> int:
    try:
        v = float(str(v).strip().rstrip("%"))
    except (TypeError, ValueError):
        return 0
    if 0 < v <= 1:  # model returned a fraction such as 0.82
        v *= 100
    return int(round(max(0, min(100, v))))


def _to_str_list(v: Any) -> List[str]:
    """Accept a list of strings/objects, or a single string, and return a clean list of strings."""
    if v is None:
        return []
    if isinstance(v, str):
        v = [p for p in v.split("\n") if p.strip()]
    if not isinstance(v, list):
        v = [v]
    out = []
    for item in v:
        if isinstance(item, dict):
            # e.g. {"degree": "...", "institution": "...", "year": "..."} -> "... | ... | ..."
            item = " | ".join(str(x) for x in item.values() if x not in (None, "", []))
        item = str(item).strip()
        if item:
            out.append(item)
    return out


class Candidate(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    education: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

    @field_validator("name", "email", "phone", mode="before")
    @classmethod
    def _str(cls, v):
        return "" if v is None else str(v).strip()

    @field_validator("education", "experience", "projects", "certifications", mode="before")
    @classmethod
    def _list(cls, v):
        return _to_str_list(v)


class SectionScores(BaseModel):
    skills: int = 0
    experience: int = 0
    education: int = 0
    projects: int = 0
    formatting: int = 0

    @field_validator("*", mode="before")
    @classmethod
    def _score(cls, v):
        return _clamp_score(v)


class AnalysisResult(BaseModel):
    candidate: Candidate = Field(default_factory=Candidate)
    match_score: int = 0
    ats_score: int = 0
    section_scores: SectionScores = Field(default_factory=SectionScores)
    skills_found: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    summary: str = ""

    @field_validator("match_score", "ats_score", mode="before")
    @classmethod
    def _score(cls, v):
        return _clamp_score(v)

    @field_validator("skills_found", "missing_skills", "strengths", "suggestions", mode="before")
    @classmethod
    def _list(cls, v):
        # de-duplicate while preserving order (case-insensitive)
        seen, out = set(), []
        for s in _to_str_list(v):
            if s.lower() not in seen:
                seen.add(s.lower())
                out.append(s)
        return out

    @field_validator("summary", mode="before")
    @classmethod
    def _summary(cls, v):
        return "" if v is None else str(v).strip()
