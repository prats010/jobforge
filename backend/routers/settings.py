"""
JobForge — Settings Router
API key management and configuration endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import BaseResume
from schemas import SettingsRead, ValidateKeyRequest, ValidateKeyResponse
from config import settings
from services.groq_service import groq_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def get_settings(db: Session = Depends(get_db)):
    """Get current application settings."""
    # Check if API key is set
    key = getattr(settings, 'GROQ_API_KEY', '')
    key_set = bool(key and len(key) > 4)
    key_preview = f"...{key[-4:]}" if key_set else ""

    # Resume preview
    resume = db.query(BaseResume).order_by(BaseResume.id.desc()).first()
    resume_preview = resume.content_md[:200] if resume else ""

    return SettingsRead(
        groq_key_set=key_set,
        groq_key_preview=key_preview,
        resume_preview=resume_preview,
        default_keywords=settings.default_keywords_list,
        greenhouse_companies=settings.greenhouse_companies_list,
        lever_companies=settings.lever_companies_list,
    )


@router.post("/validate-key", response_model=ValidateKeyResponse)
def validate_key(request: ValidateKeyRequest):
    """Test if a Groq API key is valid."""
    try:
        is_valid = groq_service.validate_api_key(request.api_key)
        if is_valid:
            # Re-configure the service with the new key
            groq_service.configure(request.api_key)
            return ValidateKeyResponse(valid=True, message="API key is valid! Groq is ready.")
        else:
            return ValidateKeyResponse(valid=False, message="API key is invalid or Groq returned an error.")
    except Exception as e:
        return ValidateKeyResponse(valid=False, message=f"Validation error: {str(e)}")
