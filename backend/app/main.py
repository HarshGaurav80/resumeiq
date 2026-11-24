"""
ResumeIQ – FastAPI application entry point.

Run from the backend/ folder:
    uvicorn app.main:app --reload --port 8000
Interactive API docs: http://localhost:8000/docs
"""
import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from . import database
from .config import JOB_ROLES, settings
from .services.ai_analyzer import AIAnalysisError, analyze_with_ai
from .services.fallback_analyzer import analyze_offline
from .services.parser import ResumeParseError, extract_text
from .services.report import build_pdf_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s: %(message)s")
log = logging.getLogger("resumeiq")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Runs once at startup: create the SQLite table and log which AI provider is active."""
    database.init_db()
    log.info("AI provider: %s", settings.active_provider)
    yield


app = FastAPI(title="ResumeIQ API", version="1.0.0", lifespan=lifespan,
              description="AI Resume Analyzer – upload a resume and a job description to get a match report.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------------------
# Meta endpoints
# --------------------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "ai_provider": settings.active_provider}


@app.get("/api/roles")
def roles():
    return {"roles": JOB_ROLES}


# --------------------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------------------

@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX, max 5 MB)"),
    job_description: str = Form(..., description="Job description text"),
    job_role: str = Form("", description="Optional job role"),
):
    # ---- Validate inputs ----------------------------------------------------------
    filename = Path(file.filename or "resume").name
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type. Please upload a PDF or DOCX resume.")

    data = await file.read(settings.MAX_FILE_SIZE + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > settings.MAX_FILE_SIZE:
        raise HTTPException(413, "File is too large. Maximum size is 5 MB.")

    job_description = (job_description or "").strip()
    if not job_description:
        raise HTTPException(400, "Please paste a job description.")
    if len(job_description) < settings.MIN_JD_LENGTH:
        raise HTTPException(400, f"Job description is too short (minimum {settings.MIN_JD_LENGTH} characters).")
    job_role = (job_role or "").strip()[:80]

    # ---- Extract resume text (CPU-bound -> thread pool) ---------------------------------
    try:
        resume_text = await run_in_threadpool(extract_text, filename, data)
    except ResumeParseError as exc:
        raise HTTPException(422, str(exc))

    # ---- Analyse: AI first, offline fallback on any failure ------------------------------
    method, notice = "offline", None
    try:
        result, method = await analyze_with_ai(resume_text, job_description, job_role)
    except AIAnalysisError as exc:
        if settings.active_provider != "none":
            log.warning("AI analysis failed, using offline fallback: %s", exc)
            notice = "AI service was unavailable, so the offline analyzer was used."
        result = await run_in_threadpool(analyze_offline, resume_text, job_description, job_role)

    record = database.save_analysis(filename, job_role, job_description, result.model_dump(), method)
    if notice:
        record["notice"] = notice
    return record


# --------------------------------------------------------------------------------------
# History
# --------------------------------------------------------------------------------------

@app.get("/api/history")
def history():
    return {"items": database.list_analyses()}


@app.get("/api/history/{analysis_id}")
def history_item(analysis_id: int):
    record = database.get_analysis(analysis_id)
    if not record:
        raise HTTPException(404, "Analysis not found.")
    return record


@app.delete("/api/history/{analysis_id}")
def delete_history_item(analysis_id: int):
    if not database.delete_analysis(analysis_id):
        raise HTTPException(404, "Analysis not found.")
    return {"deleted": analysis_id}


@app.get("/api/history/{analysis_id}/report")
def download_report(analysis_id: int):
    record = database.get_analysis(analysis_id)
    if not record:
        raise HTTPException(404, "Analysis not found.")
    pdf = build_pdf_report(record)
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(record["file_name"]).stem)[:50] or "resume"
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="ResumeIQ_Report_{stem}.pdf"'})
