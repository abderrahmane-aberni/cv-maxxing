"""FastAPI app for Resolve: upload a CV + job description, get a
structured skills-gap report, ATS match score, and bullet rewrite
suggestions back from Gemini."""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Analysis, get_db, init_db
from .gemini_client import GeminiOutputError, analyze
from .pdf_parser import PDFTextExtractionError, extract_text_from_pdf
from .schemas import AnalyzeResponse, HistoryItem, HistoryListResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resolve", description="AI CV & job-fit analyser", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo project; tighten before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_cv(
    cv_file: UploadFile = File(..., description="CV as a PDF"),
    job_description: str = Form(..., min_length=20),
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    settings = get_settings()

    if cv_file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(400, "cv_file must be a PDF.")

    raw = await cv_file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(400, f"PDF exceeds the {settings.max_upload_mb}MB limit.")

    try:
        cv_text = extract_text_from_pdf(raw)
    except PDFTextExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc

    try:
        result, usage = analyze(cv_text, job_description)
    except GeminiOutputError as exc:
        raise HTTPException(502, str(exc)) from exc

    record = Analysis(
        cv_filename=cv_file.filename or "cv.pdf",
        job_title_snippet=job_description.strip()[:120],
        ats_match_score=result.ats_match_score,
        model=usage.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        estimated_cost_usd=str(usage.estimated_cost_usd),
        result_json=result.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return AnalyzeResponse(id=record.id, created_at=record.created_at, result=result, usage=usage)


@app.get("/api/history", response_model=HistoryListResponse)
def history(db: Session = Depends(get_db), limit: int = 20) -> HistoryListResponse:
    rows = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .limit(min(limit, 100))
        .all()
    )
    items = [
        HistoryItem(
            id=row.id,
            created_at=row.created_at,
            cv_filename=row.cv_filename,
            job_title_snippet=row.job_title_snippet,
            ats_match_score=row.ats_match_score,
            model=row.model,
        )
        for row in rows
    ]
    return HistoryListResponse(items=items)


@app.get("/api/history/{analysis_id}")
def history_detail(analysis_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if row is None:
        raise HTTPException(404, "Not found.")
    return {
        "id": row.id,
        "created_at": row.created_at,
        "cv_filename": row.cv_filename,
        "result": row.result_json,
        "usage": {
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "estimated_cost_usd": row.estimated_cost_usd,
            "model": row.model,
        },
    }
