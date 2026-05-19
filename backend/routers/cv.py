"""
JobForge — CV Router
Resume management and CV tailoring endpoints.
"""

import asyncio
import io
import logging
import pypdf

from pdfminer.high_level import extract_text_to_fp, extract_pages
from pdfminer.layout import LAParams, LTTextBox
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Job, BaseResume
from schemas import BaseResumeRead, BaseResumeUpdate, TailorResult
from services.cv_tailor import tailor_resume_for_job
from services.groq_service import groq_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["cv"])


# ---------------------------------------------------------------------------
# PDF extraction helper
# ---------------------------------------------------------------------------

def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF preserving the visual structure.

    Uses pdfminer's LTTextBox objects and their Y-coordinates to detect
    visual spacing between entries (e.g. MSc vs BSc, one job vs another).
    A blank line is inserted whenever the vertical gap between consecutive
    text boxes exceeds 6 pt — the same gap that visually separates entries
    in the rendered PDF.

    Fallback chain: extract_text_to_fp → pypdf (layout mode) → pypdf (plain).
    """
    try:
        all_boxes = []
        laparams = LAParams(char_margin=2.0, line_margin=0.5, word_margin=0.1)

        for page_num, page_layout in enumerate(
            extract_pages(io.BytesIO(pdf_bytes), laparams=laparams)
        ):
            page_height = page_layout.height
            for element in page_layout:
                if isinstance(element, LTTextBox):
                    text = element.get_text().strip()
                    if not text:
                        continue
                    # pdfminer uses bottom-up coords; convert to top-down
                    y_top    = page_height - element.y1
                    y_bottom = page_height - element.y0
                    all_boxes.append({
                        "page":     page_num,
                        "y_top":    y_top,
                        "y_bottom": y_bottom,
                        "text":     text,
                    })

        if not all_boxes:
            raise ValueError("No text boxes found")

        # Sort top-to-bottom within each page
        all_boxes.sort(key=lambda b: (b["page"], b["y_top"]))

        result_parts: list[str] = []
        prev_bottom: float | None = None
        prev_page:   int   | None = None

        for box in all_boxes:
            if prev_bottom is not None:
                if box["page"] != prev_page:
                    result_parts.append("")          # page boundary → blank line
                else:
                    gap = box["y_top"] - prev_bottom
                    if gap > 6:                      # >6 pt gap = visual separator
                        result_parts.append("")

            for line in box["text"].splitlines():
                line = line.strip()
                if line:
                    result_parts.append(line)

            prev_bottom = box["y_bottom"]
            prev_page   = box["page"]

        raw = "\n".join(result_parts)
        logger.info(
            f"Position-aware PDF extraction: {len(all_boxes)} boxes, "
            f"{len(raw)} chars."
        )
        return raw

    except Exception as primary_err:
        logger.warning(
            f"Position-aware extraction failed ({primary_err}), "
            f"falling back to extract_text_to_fp"
        )

    # Fallback 1: flat pdfminer extraction
    try:
        output = StringIO()
        extract_text_to_fp(
            io.BytesIO(pdf_bytes),
            output,
            laparams=LAParams(char_margin=2.0, line_margin=0.5, word_margin=0.1),
            output_type="text",
            codec="utf-8",
        )
        result = output.getvalue()
        logger.info("Fell back to extract_text_to_fp.")
        return result
    except Exception as secondary_err:
        logger.warning(
            f"extract_text_to_fp failed ({secondary_err}), "
            f"falling back to pypdf"
        )

    # Fallback 2: pypdf
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for page in reader.pages:
        try:
            t = page.extract_text(extraction_mode="layout")
        except TypeError:
            t = page.extract_text()
        if t:
            pages.append(t)
    logger.info("Fell back to pypdf extraction.")
    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/base", response_model=BaseResumeRead)
def get_base_resume(db: Session = Depends(get_db)):
    """Get the current base resume."""
    resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No base resume found")
    return resume


@router.put("/base", response_model=BaseResumeRead)
def update_base_resume(data: BaseResumeUpdate, db: Session = Depends(get_db)):
    """Update the base resume."""
    resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
    if resume:
        resume.content_md = data.content_md
    else:
        resume = BaseResume(content_md=data.content_md)
        db.add(resume)

    db.commit()
    db.refresh(resume)
    return resume


@router.post("/upload-pdf", response_model=BaseResumeRead)
async def upload_pdf_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a PDF resume:
      1. Extract text with position-aware layout (Y-coord gap detection)
      2. Pass the raw text through AI to convert it into clean Markdown
      3. Store the clean Markdown as the base resume
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        file_bytes = await file.read()

        # ── Step 1: Extract (blocking I/O → run in thread) ────────────────────
        raw_text = await asyncio.to_thread(_extract_pdf_text, file_bytes)

        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract any text from the PDF"
            )

        logger.info(f"PDF raw text: {len(raw_text)} chars.")

        # ── Step 2: AI structuring → clean Markdown (blocking → thread) ───────
        if groq_service.is_configured:
            structured_md = await asyncio.to_thread(
                groq_service.structure_resume_text, raw_text
            )
            logger.info("PDF text structured by AI successfully.")
        else:
            structured_md = raw_text
            logger.warning("Groq not configured; saving raw extracted text.")

        # ── Step 3: Persist ───────────────────────────────────────────────────
        resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
        if resume:
            resume.content_md = structured_md
        else:
            resume = BaseResume(content_md=structured_md)
            db.add(resume)

        db.commit()
        db.refresh(resume)
        return resume

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.post("/tailor/{job_id}", response_model=TailorResult)
def tailor_cv(job_id: int, db: Session = Depends(get_db)):
    """Tailor the base resume for a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.jd_raw:
        raise HTTPException(status_code=400, detail="Job has no description")

    resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No base resume found")

    keywords = []
    if job.score_breakdown and isinstance(job.score_breakdown, dict):
        pass  # future: pull keywords_to_add from evaluation

    try:
        result = tailor_resume_for_job(
            resume=resume.content_md,
            job_description=job.jd_raw,
            keywords=keywords,
        )

        job.tailored_cv_md = result["tailored_md"]
        db.commit()

        return TailorResult(
            job_id=job.id,
            tailored_md=result["tailored_md"],
            keywords_injected=result["keywords_injected"],
            changes_summary=result["changes_summary"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tailored/{job_id}")
def get_tailored_cv(job_id: int, db: Session = Depends(get_db)):
    """Get the tailored CV for a job (if exists)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.tailored_cv_md:
        raise HTTPException(
            status_code=404,
            detail="No tailored CV exists for this job. Tailor it first."
        )
    return {"job_id": job.id, "tailored_md": job.tailored_cv_md}


@router.put("/tailored/{job_id}")
def update_tailored_cv(job_id: int, data: BaseResumeUpdate, db: Session = Depends(get_db)):
    """Manually update a tailored CV."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.tailored_cv_md = data.content_md
    db.commit()
    return {"job_id": job.id, "tailored_md": job.tailored_cv_md}
