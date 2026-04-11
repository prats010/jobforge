"""
JobForge — Scanner Router
Endpoints for triggering scans, listing sources, and scan history.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import asyncio
import logging

from database import get_db
from models import Job, ScanSession
from schemas import ScanRequest, ScanResult, SourceStatus, ScanSessionRead
from config import settings

from services.scrapers.greenhouse import scrape_greenhouse
from services.scrapers.lever import scrape_lever
from services.scrapers.internshala import scrape_internshala
from services.scrapers.linkedin import scrape_linkedin
from services.scrapers.naukri import scrape_naukri

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scanner", tags=["scanner"])

# Scraper registry
SCRAPERS = {
    "greenhouse": {
        "func": scrape_greenhouse,
        "name": "Greenhouse",
        "status": "ready",
        "description": "Public JSON API — reliable, no auth needed",
    },
    "lever": {
        "func": scrape_lever,
        "name": "Lever",
        "status": "ready",
        "description": "Public JSON API — reliable, no auth needed",
    },
    "internshala": {
        "func": scrape_internshala,
        "name": "Internshala",
        "status": "ready",
        "description": "Best-effort HTML scraping — may be blocked",
    },
    "linkedin": {
        "func": scrape_linkedin,
        "name": "LinkedIn",
        "status": "stub",
        "description": "Stub — LinkedIn blocks scrapers. Use 'Paste JD' instead",
    },
    "naukri": {
        "func": scrape_naukri,
        "name": "Naukri",
        "status": "stub",
        "description": "Stub — Naukri has anti-bot protection. Use 'Paste JD' instead",
    },
}


@router.post("/run", response_model=ScanResult)
async def run_scan(request: ScanRequest, db: Session = Depends(get_db)):
    """Trigger a scan across selected sources."""
    total_found = 0
    total_new = 0
    details = []

    for source_key in request.sources:
        if source_key not in SCRAPERS:
            details.append({
                "source": source_key,
                "status": "error",
                "message": f"Unknown source: {source_key}",
                "jobs_found": 0,
                "new_jobs": 0,
            })
            continue

        scraper = SCRAPERS[source_key]
        logger.info(f"Running {scraper['name']} scanner...")

        try:
            # Call the scraper
            if source_key == "greenhouse":
                jobs = await scraper["func"](
                    companies=settings.greenhouse_companies_list,
                    keywords=request.keywords,
                )
            elif source_key == "lever":
                jobs = await scraper["func"](
                    companies=settings.lever_companies_list,
                    keywords=request.keywords,
                )
            else:
                jobs = await scraper["func"](keywords=request.keywords)

            source_found = len(jobs)
            source_new = 0

            # Insert into database with dedup
            for job_data in jobs:
                dedup_hash = Job.compute_dedup_hash(
                    job_data.get("title", ""),
                    job_data.get("company", ""),
                )

                # Check if already exists
                existing = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()
                if existing:
                    continue

                job = Job(
                    title=job_data.get("title", ""),
                    company=job_data.get("company", ""),
                    location=job_data.get("location"),
                    job_type=job_data.get("job_type"),
                    domain=job_data.get("domain"),
                    source=job_data.get("source", scraper["name"]),
                    source_url=job_data.get("source_url"),
                    jd_raw=job_data.get("jd_raw"),
                    salary_range=job_data.get("salary_range"),
                    posted_at=job_data.get("posted_at"),
                    scraped_at=job_data.get("scraped_at", datetime.utcnow()),
                    dedup_hash=dedup_hash,
                    status="discovered",
                )
                db.add(job)
                source_new += 1

            db.commit()

            total_found += source_found
            total_new += source_new

            details.append({
                "source": scraper["name"],
                "status": "success",
                "jobs_found": source_found,
                "new_jobs": source_new,
            })
            logger.info(f"{scraper['name']}: Found {source_found}, New {source_new}")

        except Exception as e:
            logger.error(f"Scanner error for {source_key}: {e}")
            details.append({
                "source": scraper["name"],
                "status": "error",
                "message": str(e),
                "jobs_found": 0,
                "new_jobs": 0,
            })

    # Record scan session
    session = ScanSession(
        source=",".join(request.sources),
        query=",".join(request.keywords),
        jobs_found=total_found,
        new_jobs=total_new,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return ScanResult(
        jobs_found=total_found,
        new_jobs=total_new,
        scan_session_id=session.id,
        details=details,
    )


@router.get("/sources", response_model=List[SourceStatus])
def get_sources(db: Session = Depends(get_db)):
    """List all configured sources with their status."""
    sources = []
    for key, scraper in SCRAPERS.items():
        # Get last scan time for this source
        last_session = db.query(ScanSession).filter(
            ScanSession.source.contains(key)
        ).order_by(ScanSession.ran_at.desc()).first()

        sources.append(SourceStatus(
            name=scraper["name"],
            slug=key,
            enabled=scraper["status"] != "stub",
            status=scraper["status"],
            last_scanned=last_session.ran_at if last_session else None,
            description=scraper["description"],
        ))

    return sources


@router.get("/history", response_model=List[ScanSessionRead])
def get_scan_history(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List past scan sessions."""
    sessions = db.query(ScanSession).order_by(
        ScanSession.ran_at.desc()
    ).limit(limit).all()
    return sessions
