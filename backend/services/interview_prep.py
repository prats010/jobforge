"""
JobForge — Interview Prep Service
STAR story generation logic.
"""

import logging
from typing import Dict, Any, List
from services.groq_service import groq_service

logger = logging.getLogger(__name__)


def generate_star_stories(resume: str, job_description: str) -> List[Dict[str, Any]]:
    """
    Generate STAR+Reflection interview stories using Gemini AI.
    """
    if not groq_service.is_configured:
        raise RuntimeError("Groq API key not configured.")

    if not resume or not resume.strip():
        raise ValueError("Base resume is empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty.")

    logger.info("Generating STAR interview stories...")

    try:
        stories = groq_service.generate_star_stories(resume, job_description)

        if not isinstance(stories, list):
            raise RuntimeError("AI did not return a list of stories")

        # Validate each story has required fields
        required = ["question", "situation", "task", "action", "result", "reflection"]
        validated = []
        for story in stories:
            if isinstance(story, dict) and all(k in story for k in required):
                validated.append(story)

        if not validated:
            raise RuntimeError("AI returned stories in invalid format")

        logger.info(f"Generated {len(validated)} STAR stories")
        return validated

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"STAR story generation failed: {e}")
        raise RuntimeError(f"STAR story generation failed: {e}")
