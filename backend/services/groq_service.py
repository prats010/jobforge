"""
JobForge — Groq AI Service
Wrapper for Groq API (Llama 3 70B) with retry logic and structured outputs.
"""

import json
import time
import logging
from typing import Optional
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)


class GroqService:
    """Async-compatible wrapper for Groq Llama 3 API."""

    def __init__(self):
        self.client = None
        self._configured = False

    def configure(self, api_key: Optional[str] = None):
        """Configure the Groq client with API key."""
        key = api_key or getattr(settings, 'GROQ_API_KEY', None)
        if not key:
            logger.warning("No Groq API key configured")
            return
        
        try:
            self.client = Groq(api_key=key)
            self._configured = True
            logger.info("Groq service configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Groq: {e}")

    @property
    def is_configured(self) -> bool:
        return self._configured and self.client is not None

    def _call_with_retry(self, prompt: str, max_retries: int = 3, is_json: bool = True) -> str:
        """Call Groq with exponential backoff retry for rate limits."""
        if not self.is_configured:
            raise RuntimeError("Groq service not configured. Set GROQ_API_KEY")

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a highly capable AI assistant. Always return valid JSON when requested."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    response_format={"type": "json_object"} if is_json else None
                )
                
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
                else:
                    raise RuntimeError("Groq returned empty response")
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "rate" in error_str:
                    wait_time = (2 ** attempt) * 2
                    logger.warning(f"Groq Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif "api key" in error_str or "auth" in error_str or "key" in error_str:
                    raise RuntimeError(f"Invalid Groq API key: {e}")
                else:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Groq API error after {max_retries} attempts: {e}")
                    time.sleep(1)
                    continue

        raise RuntimeError("Groq API failed after all retries")

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Groq response."""
        text = text.strip()
        if text.startswith("```json"): text = text[7:]
        elif text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {text[:500]}")
            raise RuntimeError(f"Failed to parse AI response as JSON: {e}")

    def evaluate_job(self, job_description: str, resume: str) -> dict:
        prompt = f"""You are an expert career advisor and job matching AI. Evaluate the job match. Return ONLY a valid JSON object matching the requested schema exactly.

Candidate Resume:
{resume}

Job Description:
{job_description}

Score the match across 10 dimensions (0.0 to 5.0): technical_skills_match, domain_alignment, experience_level_fit, project_portfolio_relevance, growth_potential, company_quality, location_remote_compatibility, compensation_estimate, tech_stack_modernity, application_success_probability.
Calculate overall numeric_score and letter_grade (A/B/C/D/F).

JSON Schema matching the output:
{{
    "letter_grade": "B",
    "numeric_score": 3.7,
    "dimensions": {{"technical_skills_match": 4.0, "domain_alignment": 3.5, ...}},
    "strengths": ["...", "..."],
    "gaps": ["...", "..."],
    "recommendation": "...",
    "keywords_to_add": ["...", "..."],
    "one_liner": "..."
}}"""
        return self._extract_json(self._call_with_retry(prompt))

    def extract_job_details(self, jd_text: str) -> dict:
        prompt = f"""Extract structured job details. Return ONLY valid JSON:
{jd_text}

JSON Schema expected:
{{
    "title": "...",
    "company": "...",
    "location": "...",
    "job_type": "...",
    "domain": "...",
    "salary_range": "...",
    "summary": "..."
}}"""
        return self._extract_json(self._call_with_retry(prompt))

    def tailor_resume(self, resume: str, job_description: str, keywords: list) -> dict:
        keywords_str = ", ".join(keywords) if keywords else "None specified"
        prompt = f"""You are a resume writer. Rewrite this Markdown resume to match the job description, injecting keywords naturally. 
        
CRITICAL RULES:
1. Keep the layout IDENTICAL to the original. Do not merge lines. 
2. Use standard bullet points (-) wherever lists appear.
3. DO NOT use all caps for body text. Use standard sentence casing.
4. Separate sections with newlines. Do not boldly clump info together.

Resume:
{resume}
Job Description:
{job_description}
Keywords to add:
{keywords_str}

Return ONLY valid JSON:
{{
    "tailored_resume_md": "# Full tailored resume in markdown...",
    "keywords_injected": ["..."],
    "changes_summary": "..."
}}"""
        return self._extract_json(self._call_with_retry(prompt))

    def generate_star_stories(self, resume: str, job_description: str) -> list:
        prompt = f"""You are an interview coach. Generate 5 distinct behavioral STAR stories (Situation, Task, Action, Result, Reflection - each a paragraph) based on the candidate's actual projects.

Resume:
{resume}
Job Description:
{job_description}

Return ONLY this exact JSON schema:
{{"stories": [
    {{
        "question": "Tell me about a time you...",
        "situation": "...",
        "task": "...",
        "action": "...",
        "result": "...",
        "reflection": "..."
    }}
]}}"""
        response = self._extract_json(self._call_with_retry(prompt))
        return response.get("stories", response)

    def validate_api_key(self, api_key: str) -> bool:
        try:
            temp_client = Groq(api_key=api_key)
            res = temp_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            return bool(res.choices)
        except Exception as e:
            logger.error(f"Groq API key validation failed: {e}")
            return False

groq_service = GroqService()
