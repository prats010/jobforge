"""
JobForge — Pydantic v2 Schemas
Request/response models for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ──────────────────────────── Job Schemas ────────────────────────────

class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    domain: Optional[str] = None
    source: Optional[str] = "Manual"
    source_url: Optional[str] = None
    jd_raw: Optional[str] = None
    salary_range: Optional[str] = None


class JobRead(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    domain: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    jd_raw: Optional[str] = None
    jd_summary: Optional[str] = None
    salary_range: Optional[str] = None
    posted_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    status: str = "discovered"
    score_letter: Optional[str] = None
    score_numeric: Optional[float] = None
    score_breakdown: Optional[Dict[str, Any]] = None
    evaluation_md: Optional[str] = None
    tailored_cv_md: Optional[str] = None
    star_stories: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


# ──────────────────────────── Scanner Schemas ────────────────────────────

class ScanRequest(BaseModel):
    sources: List[str] = Field(default=["greenhouse", "lever"])
    keywords: List[str] = Field(default=["data scientist", "machine learning engineer", "AI intern"])


class ScanResult(BaseModel):
    jobs_found: int
    new_jobs: int
    scan_session_id: int
    details: List[Dict[str, Any]] = []


class SourceStatus(BaseModel):
    name: str
    slug: str
    enabled: bool = True
    status: str = "ready"  # ready, scanning, error, stub
    last_scanned: Optional[datetime] = None
    description: str = ""


class ScanSessionRead(BaseModel):
    id: int
    source: Optional[str] = None
    query: Optional[str] = None
    jobs_found: int = 0
    new_jobs: int = 0
    ran_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Evaluator Schemas ────────────────────────────

class EvaluationResult(BaseModel):
    job_id: int
    letter_grade: str
    numeric_score: float
    dimensions: Dict[str, float]
    strengths: List[str]
    gaps: List[str]
    recommendation: str
    keywords_to_add: List[str]
    one_liner: str


class BulkEvaluateRequest(BaseModel):
    job_ids: List[int]


class PasteJDRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    jd_text: str
    source_url: Optional[str] = None


# ──────────────────────────── CV Schemas ────────────────────────────

class BaseResumeRead(BaseModel):
    id: int
    content_md: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BaseResumeUpdate(BaseModel):
    content_md: str


class TailoredCVUpdate(BaseModel):
    tailored_cv_md: str


class TailorResult(BaseModel):
    job_id: int
    tailored_md: str
    keywords_injected: List[str]
    changes_summary: str


# ──────────────────────────── Interview Schemas ────────────────────────────

class STARStory(BaseModel):
    question: str
    situation: str
    task: str
    action: str
    result: str
    reflection: str


class InterviewPrepResult(BaseModel):
    job_id: int
    stories: List[STARStory]


# ──────────────────────────── Settings Schemas ────────────────────────────

class SettingsRead(BaseModel):
    groq_key_set: bool
    groq_key_preview: str = ""  # last 4 chars
    resume_preview: str = ""      # first 200 chars
    default_keywords: List[str] = []
    greenhouse_companies: List[str] = []
    lever_companies: List[str] = []


class ValidateKeyRequest(BaseModel):
    api_key: str


class ValidateKeyResponse(BaseModel):
    valid: bool
    message: str


# ──────────────────────────── Stats Schemas ────────────────────────────

class JobStats(BaseModel):
    total_jobs: int = 0
    evaluated: int = 0
    applied: int = 0
    interviews: int = 0
    status_counts: Dict[str, int] = {}
    score_distribution: Dict[str, int] = {}
    domain_breakdown: Dict[str, int] = {}
    source_breakdown: Dict[str, int] = {}
