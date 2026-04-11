"""
JobForge — Tracker Router
Application tracking / Kanban board endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
import logging

from database import get_db
from models import Job
from schemas import JobRead, JobUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tracker", tags=["tracker"])

# Valid statuses for Kanban columns
VALID_STATUSES = [
    "discovered", "evaluating", "shortlisted",
    "applied", "interview", "offer", "rejected"
]


@router.get("/board")
def get_board(db: Session = Depends(get_db)):
    """Return all jobs grouped by status for Kanban board."""
    board = {}
    for status in VALID_STATUSES:
        jobs = db.query(Job).filter(Job.status == status).order_by(
            Job.updated_at.desc()
        ).all()
        board[status] = [JobRead.model_validate(job) for job in jobs]

    return board


@router.patch("/move/{job_id}")
def move_job(job_id: int, data: JobUpdate, db: Session = Depends(get_db)):
    """Move a job to a new status."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    if data.status:
        job.status = data.status
    if data.notes:
        job.notes = data.notes

    db.commit()
    db.refresh(job)
    return JobRead.model_validate(job)


@router.post("/notes/{job_id}")
def add_notes(job_id: int, data: JobUpdate, db: Session = Depends(get_db)):
    """Add or update notes for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if data.notes is not None:
        job.notes = data.notes

    db.commit()
    db.refresh(job)
    return {"message": "Notes updated", "job_id": job_id}
