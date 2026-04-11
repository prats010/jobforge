"""
JobForge — Evaluator Router
AI job evaluation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from models import Job, BaseResume
from schemas import EvaluationResult, BulkEvaluateRequest, PasteJDRequest, JobRead
from services.evaluator import evaluate_job_vs_resume
from services.groq_service import groq_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/evaluator", tags=["evaluator"])


def _get_base_resume(db: Session) -> str:
    """Get the current base resume markdown."""
    resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No base resume found. Go to Settings to add your resume.")
    return resume.content_md


@router.post("/evaluate/{job_id}", response_model=EvaluationResult)
def evaluate_job(job_id: int, db: Session = Depends(get_db)):
    """Evaluate a single job against the base resume."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.jd_raw:
        raise HTTPException(status_code=400, detail="Job has no description text. Cannot evaluate.")

    resume = _get_base_resume(db)

    try:
        result = evaluate_job_vs_resume(job.jd_raw, resume)

        # Save evaluation to job
        job.score_letter = result["letter_grade"]
        job.score_numeric = result["numeric_score"]
        job.score_breakdown = result["dimensions"]
        job.evaluation_md = result.get("recommendation", "")
        if job.status == "discovered":
            job.status = "evaluating"

        db.commit()
        db.refresh(job)

        return EvaluationResult(
            job_id=job.id,
            letter_grade=result["letter_grade"],
            numeric_score=result["numeric_score"],
            dimensions=result["dimensions"],
            strengths=result["strengths"],
            gaps=result["gaps"],
            recommendation=result["recommendation"],
            keywords_to_add=result["keywords_to_add"],
            one_liner=result["one_liner"],
        )

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


@router.post("/evaluate-bulk")
def evaluate_bulk(request: BulkEvaluateRequest, db: Session = Depends(get_db)):
    """Evaluate multiple jobs. Processes sequentially to respect rate limits."""
    resume = _get_base_resume(db)
    results = []
    errors = []

    for job_id in request.job_ids:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            errors.append({"job_id": job_id, "error": "Job not found"})
            continue

        if not job.jd_raw:
            errors.append({"job_id": job_id, "error": "No job description"})
            continue

        try:
            result = evaluate_job_vs_resume(job.jd_raw, resume)

            # Save to DB
            job.score_letter = result["letter_grade"]
            job.score_numeric = result["numeric_score"]
            job.score_breakdown = result["dimensions"]
            job.evaluation_md = result.get("recommendation", "")
            if job.status == "discovered":
                job.status = "evaluating"

            db.commit()

            results.append({
                "job_id": job.id,
                "letter_grade": result["letter_grade"],
                "numeric_score": result["numeric_score"],
                "one_liner": result["one_liner"],
            })

        except Exception as e:
            errors.append({"job_id": job_id, "error": str(e)})

    return {"results": results, "errors": errors, "total": len(results)}


@router.post("/paste-evaluate", response_model=EvaluationResult)
def paste_and_evaluate(request: PasteJDRequest, db: Session = Depends(get_db)):
    """Paste a JD, extract details, save as job, and evaluate."""
    resume = _get_base_resume(db)

    # Try to extract job details from JD text
    title = request.title
    company = request.company

    if not title or not company:
        try:
            extracted = groq_service.extract_job_details(request.jd_text)
            title = title or extracted.get("title", "Untitled Position")
            company = company or extracted.get("company", "Unknown Company")
        except Exception:
            title = title or "Untitled Position"
            company = company or "Unknown Company"

    # Create the job
    dedup_hash = Job.compute_dedup_hash(title, company)
    existing = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()

    if existing:
        job = existing
        job.jd_raw = request.jd_text  # Update JD if re-pasted
    else:
        job = Job(
            title=title,
            company=company,
            source="Manual",
            source_url=request.source_url,
            jd_raw=request.jd_text,
            dedup_hash=dedup_hash,
            status="discovered",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

    # Now evaluate
    try:
        result = evaluate_job_vs_resume(request.jd_text, resume)

        job.score_letter = result["letter_grade"]
        job.score_numeric = result["numeric_score"]
        job.score_breakdown = result["dimensions"]
        job.evaluation_md = result.get("recommendation", "")
        job.status = "evaluating"

        db.commit()
        db.refresh(job)

        return EvaluationResult(
            job_id=job.id,
            letter_grade=result["letter_grade"],
            numeric_score=result["numeric_score"],
            dimensions=result["dimensions"],
            strengths=result["strengths"],
            gaps=result["gaps"],
            recommendation=result["recommendation"],
            keywords_to_add=result["keywords_to_add"],
            one_liner=result["one_liner"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
