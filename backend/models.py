"""
JobForge — SQLAlchemy ORM Models
All database tables: Job, BaseResume, ScanSession.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from database import Base
import hashlib


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)      # Full-time, Internship, Remote, Hybrid
    domain = Column(String, nullable=True)         # Data Science, ML Engineer, AI Research, etc.
    source = Column(String, nullable=True)         # LinkedIn, Naukri, Greenhouse, Lever, Manual
    source_url = Column(String, nullable=True)
    jd_raw = Column(Text, nullable=True)           # Full job description text
    jd_summary = Column(Text, nullable=True)       # AI-generated summary
    salary_range = Column(String, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, nullable=True)

    # Application status
    status = Column(String, default="discovered")  # discovered, evaluating, shortlisted, applied, interview, offer, rejected

    # AI Evaluation
    score_letter = Column(String, nullable=True)   # A, B, C, D, F
    score_numeric = Column(Float, nullable=True)   # 0.0 to 5.0
    score_breakdown = Column(JSON, nullable=True)   # dict of 10 dimension scores
    evaluation_md = Column(Text, nullable=True)     # Full AI evaluation markdown

    # CV Tailoring
    tailored_cv_md = Column(Text, nullable=True)    # AI-tailored resume markdown

    # Interview Prep
    star_stories = Column(JSON, nullable=True)      # list of STAR story objects

    # Notes
    notes = Column(Text, nullable=True)

    # Dedup
    dedup_hash = Column(String, index=True, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @staticmethod
    def compute_dedup_hash(title: str, company: str) -> str:
        """Compute dedup hash from normalized title + company."""
        normalized = f"{title.strip().lower()}|{company.strip().lower()}"
        return hashlib.md5(normalized.encode()).hexdigest()


class BaseResume(Base):
    __tablename__ = "base_resume"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_md = Column(Text, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source = Column(String, nullable=True)
    query = Column(String, nullable=True)
    jobs_found = Column(Integer, default=0)
    new_jobs = Column(Integer, default=0)
    ran_at = Column(DateTime, server_default=func.now())
