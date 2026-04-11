"""
JobForge — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from config import settings
from database import create_tables, SessionLocal
from models import BaseResume
from services.groq_service import groq_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="JobForge API",
    description="AI-powered job search pipeline for Data Science / ML / AI roles",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routers import jobs, scanner, evaluator, cv, tracker, interview, settings as settings_router

app.include_router(jobs.router)
app.include_router(scanner.router)
app.include_router(evaluator.router)
app.include_router(cv.router)
app.include_router(tracker.router)
app.include_router(interview.router)
app.include_router(settings_router.router)


@app.on_event("startup")
def on_startup():
    """Initialize database and seed data on startup."""
    logger.info("🔨 Creating database tables...")
    create_tables()

    # Seed base resume from file if DB is empty
    db = SessionLocal()
    try:
        existing = db.query(BaseResume).first()
        if not existing:
            resume_path = os.path.join("data", "base_resume.md")
            if os.path.exists(resume_path):
                with open(resume_path, "r", encoding="utf-8") as f:
                    content = f.read()
                resume = BaseResume(content_md=content)
                db.add(resume)
                db.commit()
                logger.info("📄 Base resume seeded from file")
            else:
                logger.warning("⚠️ No base_resume.md found in data/")
        else:
            logger.info("📄 Base resume already exists in DB")
    finally:
        db.close()

    # Configure Groq
    if getattr(settings, 'GROQ_API_KEY', None):
        groq_service.configure()
        logger.info("🤖 Groq AI service configured")
    else:
        logger.warning("⚠️ No GROQ_API_KEY set — AI features disabled")

    logger.info("🚀 JobForge API ready!")


@app.get("/")
def root():
    return {
        "name": "JobForge API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "groq_configured": groq_service.is_configured}
