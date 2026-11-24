"""
Application settings, loaded once from environment variables / the .env file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# backend/ folder (one level above this package)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


class Settings:
    AI_PROVIDER = _env("AI_PROVIDER", "auto").lower()
    GEMINI_API_KEY = _env("GEMINI_API_KEY")
    GEMINI_MODEL = _env("GEMINI_MODEL", "gemini-2.5-flash")
    OPENAI_API_KEY = _env("OPENAI_API_KEY")
    OPENAI_MODEL = _env("OPENAI_MODEL", "gpt-4o-mini")
    AI_TIMEOUT = float(_env("AI_TIMEOUT", "60"))

    DATABASE_PATH = BASE_DIR / _env("DATABASE_PATH", "data/resumeiq.db")
    CORS_ORIGINS = [o.strip() for o in _env(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
    # Optional regex for extra allowed origins, e.g. every Vercel deployment of this app:
    #   CORS_ORIGIN_REGEX=https://resumeiq.*\.vercel\.app
    CORS_ORIGIN_REGEX = _env("CORS_ORIGIN_REGEX") or None

    # Upload validation
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    MIN_JD_LENGTH = 30  # characters

    @property
    def active_provider(self) -> str:
        """Resolve which AI provider will actually be used ('gemini', 'openai' or 'none')."""
        p = self.AI_PROVIDER
        if p == "gemini":
            return "gemini" if self.GEMINI_API_KEY else "none"
        if p == "openai":
            return "openai" if self.OPENAI_API_KEY else "none"
        if p == "none":
            return "none"
        # auto
        if self.GEMINI_API_KEY:
            return "gemini"
        if self.OPENAI_API_KEY:
            return "openai"
        return "none"


settings = Settings()

# Job roles shown in the frontend dropdown
JOB_ROLES = [
    "Software Developer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Web Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Mobile App Developer",
    "UI/UX Designer",
    "QA / Test Engineer",
    "Cybersecurity Analyst",
    "Product Manager",
    "Business Analyst",
]
