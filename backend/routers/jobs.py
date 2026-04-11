"""
JobForge — Jobs Router
CRUD operations for jobs + stats endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from database import get_db
from models import Job
from schemas import JobCreate, JobRead, JobUpdate, JobStats

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/stats", response_model=JobStats)
def get_job_stats(db: Session = Depends(get_db)):
    """Get aggregate job statistics."""
    total = db.query(Job).count()
    evaluated = db.query(Job).filter(Job.score_letter.isnot(None)).count()
    applied = db.query(Job).filter(Job.status == "applied").count()
    interviews = db.query(Job).filter(Job.status == "interview").count()

    # Status counts
    status_rows = db.query(Job.status, func.count(Job.id)).group_by(Job.status).all()
    status_counts = {row[0] or "unknown": row[1] for row in status_rows}

    # Score distribution
    score_rows = db.query(Job.score_letter, func.count(Job.id)).filter(
        Job.score_letter.isnot(None)
    ).group_by(Job.score_letter).all()
    score_distribution = {row[0]: row[1] for row in score_rows}

    # Domain breakdown
    domain_rows = db.query(Job.domain, func.count(Job.id)).filter(
        Job.domain.isnot(None)
    ).group_by(Job.domain).all()
    domain_breakdown = {row[0]: row[1] for row in domain_rows}

    # Source breakdown
    source_rows = db.query(Job.source, func.count(Job.id)).filter(
        Job.source.isnot(None)
    ).group_by(Job.source).all()
    source_breakdown = {row[0]: row[1] for row in source_rows}

    return JobStats(
        total_jobs=total,
        evaluated=evaluated,
        applied=applied,
        interviews=interviews,
        status_counts=status_counts,
        score_distribution=score_distribution,
        domain_breakdown=domain_breakdown,
        source_breakdown=source_breakdown,
    )


@router.get("", response_model=List[JobRead])
def list_jobs(
    status: Optional[str] = Query(None),
    score_min: Optional[float] = Query(None),
    domain: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all jobs with optional filters."""
    query = db.query(Job)

    if status:
        query = query.filter(Job.status == status)
    if score_min is not None:
        query = query.filter(Job.score_numeric >= score_min)
    if domain:
        query = query.filter(Job.domain == domain)
    if source:
        query = query.filter(Job.source == source)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_term),
                Job.company.ilike(search_term),
                Job.domain.ilike(search_term),
            )
        )

    query = query.order_by(Job.created_at.desc())
    jobs = query.offset(offset).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobRead)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Manually add a job."""
    dedup_hash = Job.compute_dedup_hash(job_data.title, job_data.company)

    # Check for duplicate
    existing = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()
    if existing:
        raise HTTPException(status_code=409, detail="Job already exists (duplicate title + company)")

    job = Job(
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        job_type=job_data.job_type,
        domain=job_data.domain,
        source=job_data.source or "Manual",
        source_url=job_data.source_url,
        jd_raw=job_data.jd_raw,
        salary_range=job_data.salary_range,
        dedup_hash=dedup_hash,
        status="discovered",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": f"Job {job_id} deleted"}


@router.patch("/{job_id}", response_model=JobRead)
def update_job(job_id: int, job_data: JobUpdate, db: Session = Depends(get_db)):
    """Update job status or notes."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_data.status is not None:
        job.status = job_data.status
    if job_data.notes is not None:
        job.notes = job_data.notes

    db.commit()
    db.refresh(job)
    return job
