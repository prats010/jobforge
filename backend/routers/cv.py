"""
JobForge — CV Router
Resume management and CV tailoring endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import Job, BaseResume
from schemas import BaseResumeRead, BaseResumeUpdate, TailorResult
from services.cv_tailor import tailor_resume_for_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["cv"])


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

    # Get keywords from evaluation if available
    keywords = []
    if job.score_breakdown and isinstance(job.score_breakdown, dict):
        # The evaluation_md might have keywords, but let's use what we stored
        pass

    try:
        result = tailor_resume_for_job(
            resume=resume.content_md,
            job_description=job.jd_raw,
            keywords=keywords,
        )

        # Save tailored CV to job
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
        raise HTTPException(status_code=404, detail="No tailored CV exists for this job. Tailor it first.")
    return {"job_id": job.id, "tailored_md": job.tailored_cv_md}
