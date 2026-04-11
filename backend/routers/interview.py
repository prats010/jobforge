"""
JobForge — Interview Router
STAR story generation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import Job, BaseResume
from schemas import InterviewPrepResult
from services.interview_prep import generate_star_stories

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/generate/{job_id}", response_model=InterviewPrepResult)
def generate_stories(job_id: int, db: Session = Depends(get_db)):
    """Generate STAR stories for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.jd_raw:
        raise HTTPException(status_code=400, detail="Job has no description")

    resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No base resume found")

    try:
        stories = generate_star_stories(resume.content_md, job.jd_raw)

        # Save to job
        job.star_stories = stories
        db.commit()

        return InterviewPrepResult(job_id=job.id, stories=stories)

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stories/{job_id}", response_model=InterviewPrepResult)
def get_stories(job_id: int, db: Session = Depends(get_db)):
    """Get stored STAR stories for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.star_stories:
        raise HTTPException(status_code=404, detail="No stories generated yet")

    return InterviewPrepResult(job_id=job.id, stories=job.star_stories)
