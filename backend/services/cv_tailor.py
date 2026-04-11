"""
JobForge — CV Tailoring Service
AI-powered resume tailoring logic.
"""

import logging
from typing import Dict, Any, List
from services.groq_service import groq_service

logger = logging.getLogger(__name__)


def tailor_resume_for_job(resume: str, job_description: str, keywords: List[str] = None) -> Dict[str, Any]:
    """
    Tailor a resume for a specific job description using Gemini AI.
    """
    if not groq_service.is_configured:
        raise RuntimeError("Groq API key not configured. Go to Settings to add your key.")

    if not resume or not resume.strip():
        raise ValueError("Base resume is empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty.")

    keywords = keywords or []

    logger.info("Starting AI resume tailoring...")

    try:
        result = groq_service.tailor_resume(resume, job_description, keywords)

        # Validate
        if "tailored_resume_md" not in result:
            raise RuntimeError("AI did not return tailored resume content")

        return {
            "tailored_md": result["tailored_resume_md"],
            "keywords_injected": result.get("keywords_injected", []),
            "changes_summary": result.get("changes_summary", "Resume tailored successfully."),
        }

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"CV tailoring failed: {e}")
        raise RuntimeError(f"AI CV tailoring failed: {e}")
