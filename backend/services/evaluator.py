"""
JobForge — Evaluator Service
AI-powered job evaluation logic using Gemini.
"""

import logging
from typing import Dict, Any
from services.groq_service import groq_service

logger = logging.getLogger(__name__)


def evaluate_job_vs_resume(job_description: str, resume: str) -> Dict[str, Any]:
    """
    Evaluate a job description against the user's resume using Gemini AI.
    Returns structured evaluation with scores, strengths, gaps, and keywords.
    """
    if not groq_service.is_configured:
        raise RuntimeError("Groq API key not configured. Go to Settings to add your key.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty. Cannot evaluate.")

    if not resume or not resume.strip():
        raise ValueError("Base resume is empty. Go to Settings to add your resume.")

    logger.info("Starting AI job evaluation...")

    try:
        result = groq_service.evaluate_job(job_description, resume)

        # Validate required fields
        required_fields = ["letter_grade", "numeric_score", "dimensions", "strengths", "gaps", "recommendation", "keywords_to_add", "one_liner"]
        for field in required_fields:
            if field not in result:
                result[field] = _default_value(field)

        # Clamp numeric score
        result["numeric_score"] = max(0.0, min(5.0, float(result["numeric_score"])))

        # Validate letter grade
        valid_grades = ["A", "B", "C", "D", "F"]
        if result["letter_grade"] not in valid_grades:
            result["letter_grade"] = _score_to_grade(result["numeric_score"])

        # Ensure dimensions are float
        if isinstance(result.get("dimensions"), dict):
            result["dimensions"] = {k: max(0.0, min(5.0, float(v))) for k, v in result["dimensions"].items()}

        logger.info(f"Evaluation complete: {result['letter_grade']} ({result['numeric_score']}/5.0)")
        return result

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise RuntimeError(f"AI evaluation failed: {e}")


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 4.0:
        return "A"
    elif score >= 3.0:
        return "B"
    elif score >= 2.0:
        return "C"
    elif score >= 1.0:
        return "D"
    else:
        return "F"


def _default_value(field: str):
    """Return default values for missing fields."""
    defaults = {
        "letter_grade": "C",
        "numeric_score": 2.5,
        "dimensions": {},
        "strengths": [],
        "gaps": [],
        "recommendation": "Unable to generate full recommendation.",
        "keywords_to_add": [],
        "one_liner": "Evaluation completed with limited details.",
    }
    return defaults.get(field, "")
