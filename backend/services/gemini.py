"""
JobForge — Gemini AI Service
Wrapper for Google Gemini 1.5 Flash with retry logic and structured outputs.
"""

import google.generativeai as genai
import json
import time
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Async-compatible wrapper for Gemini 1.5 Flash."""

    def __init__(self):
        self.model = None
        self._configured = False

    def configure(self, api_key: Optional[str] = None):
        """Configure the Gemini client with API key."""
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            logger.warning("No Gemini API key configured")
            return
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self._configured = True
        logger.info("Gemini service configured successfully")

    @property
    def is_configured(self) -> bool:
        return self._configured and self.model is not None

    def _call_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini with exponential backoff retry for rate limits."""
        if not self.is_configured:
            raise RuntimeError("Gemini service not configured. Set GEMINI_API_KEY in .env")

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096,
                    ),
                )
                if response.text:
                    return response.text
                else:
                    raise RuntimeError("Gemini returned empty response")
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "rate" in error_str or "quota" in error_str:
                    wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif "api key" in error_str or "invalid" in error_str:
                    raise RuntimeError(f"Invalid Gemini API key: {e}")
                else:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Gemini API error after {max_retries} attempts: {e}")
                    time.sleep(1)
                    continue

        raise RuntimeError("Gemini API failed after all retries")

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Gemini response (handles markdown code blocks)."""
        text = text.strip()
        # Remove markdown code block wrappers
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Raw response: {text[:500]}")
            raise RuntimeError(f"Failed to parse AI response as JSON: {e}")

    def evaluate_job(self, job_description: str, resume: str) -> dict:
        """Evaluate a job description against the user's resume."""
        prompt = f"""You are an expert career advisor and job matching AI. Evaluate how well this candidate matches the given job description.

## Candidate's Resume:
{resume}

## Job Description:
{job_description}

## Instructions:
Score the match across these 10 dimensions, each from 0.0 to 5.0:
1. **Technical Skills Match** — Do the candidate's skills align with the required tech stack?
2. **Domain Alignment** — DS vs MLE vs AI Research vs Data Analyst match
3. **Experience Level Fit** — Does the candidate's experience level match? (fresher/intern/0-2yr)
4. **Project Portfolio Relevance** — Do their projects demonstrate what's needed?
5. **Growth Potential** — Does this role push the candidate forward?
6. **Company Quality** — Tier 1/2/3 company, known for ML/AI work?
7. **Location/Remote Compatibility** — Compatible with candidate's location (Pune, India)?
8. **Compensation Estimate** — Fair for their level?
9. **Tech Stack Modernity** — Using current tools (transformers, PyTorch, etc.)?
10. **Application Success Probability** — Realistic chance given their profile?

Calculate the overall numeric score as the weighted average (Technical Skills and Domain Alignment weighted 1.5x).
Assign a letter grade: A (4.0-5.0), B (3.0-3.9), C (2.0-2.9), D (1.0-1.9), F (0.0-0.9).

Return ONLY valid JSON (no markdown, no explanation outside JSON):
{{
    "letter_grade": "B",
    "numeric_score": 3.7,
    "dimensions": {{
        "technical_skills_match": 4.0,
        "domain_alignment": 3.5,
        "experience_level_fit": 3.0,
        "project_portfolio_relevance": 4.2,
        "growth_potential": 4.0,
        "company_quality": 3.5,
        "location_remote_compatibility": 3.0,
        "compensation_estimate": 3.5,
        "tech_stack_modernity": 4.0,
        "application_success_probability": 3.0
    }},
    "strengths": ["Strong Python and ML fundamentals", "Relevant NLP project experience"],
    "gaps": ["No production MLOps experience", "Missing Docker/Kubernetes skills"],
    "recommendation": "Apply — strong match on NLP projects. Highlight MindBridge AI and Titanic prediction project. Address MLOps gap in cover letter.",
    "keywords_to_add": ["MLflow", "Docker", "Airflow", "CI/CD"],
    "one_liner": "Good fit for ML Engineer role — apply with tailored resume"
}}"""

        response_text = self._call_with_retry(prompt)
        return self._extract_json(response_text)

    def extract_job_details(self, jd_text: str) -> dict:
        """Extract structured job details from raw JD text."""
        prompt = f"""Extract structured information from this job description. Return ONLY valid JSON:

## Job Description:
{jd_text}

Return:
{{
    "title": "extracted job title",
    "company": "extracted company name",
    "location": "extracted location or Remote",
    "job_type": "Full-time or Internship or Remote or Hybrid",
    "domain": "Data Science or ML Engineer or AI Research or Data Analyst or NLP Engineer or MLOps or Other",
    "salary_range": "extracted salary or null",
    "summary": "3-sentence summary of the role"
}}"""

        response_text = self._call_with_retry(prompt)
        return self._extract_json(response_text)

    def tailor_resume(self, resume: str, job_description: str, keywords: list) -> dict:
        """Tailor a resume for a specific job description."""
        keywords_str = ", ".join(keywords) if keywords else "None specified"
        prompt = f"""You are an expert resume writer. Rewrite this resume to better match the job description.

## Original Resume (Markdown):
{resume}

## Job Description:
{job_description}

## Keywords to Naturally Inject:
{keywords_str}

## Rules:
1. Keep the SAME structure and sections as the original
2. Inject the keywords naturally — don't just list them
3. Emphasize relevant projects and skills for THIS specific role
4. Maintain truthfulness — don't fabricate experience
5. Quantify achievements where possible
6. Use strong action verbs
7. Output as clean, well-formatted Markdown

Return ONLY valid JSON:
{{
    "tailored_resume_md": "# Full tailored resume in markdown...",
    "keywords_injected": ["MLflow", "Docker"],
    "changes_summary": "Brief summary of what was changed"
}}"""

        response_text = self._call_with_retry(prompt)
        return self._extract_json(response_text)

    def generate_star_stories(self, resume: str, job_description: str) -> list:
        """Generate STAR+Reflection interview stories."""
        prompt = f"""You are an expert interview coach for Data Science / ML / AI roles. Generate 5 behavioral interview STAR stories.

## Candidate's Resume:
{resume}

## Target Job Description:
{job_description}

## Instructions:
Generate 5 STAR+Reflection stories based on the candidate's ACTUAL experience and projects.
Each story should map to a common DS/ML interview question.
Make the stories realistic, specific, and detailed.

Return ONLY valid JSON array:
[
    {{
        "question": "Tell me about a time you dealt with messy data",
        "situation": "During my internship at Syntecxhub, I was assigned to analyze IPL cricket data...",
        "task": "I needed to clean and prepare the dataset for meaningful analysis...",
        "action": "I built a data cleaning pipeline using Pandas...",
        "result": "The cleaned dataset revealed clear patterns in player performance...",
        "reflection": "This experience taught me the importance of data quality..."
    }}
]"""

        response_text = self._call_with_retry(prompt)
        return self._extract_json(response_text)

    def validate_api_key(self, api_key: str) -> bool:
        """Test if a Gemini API key is valid."""
        try:
            genai.configure(api_key=api_key)
            # Try multiple model names in case one is deprecated
            model_names = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro", "models/gemini-2.0-flash"]
            for model_name in model_names:
                try:
                    logger.info(f"Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Say OK")
                    if response.text:
                        logger.info(f"SUCCESS with model: {model_name}")
                        return True
                except Exception as inner_e:
                    logger.warning(f"Model {model_name} failed: {inner_e}")
                    continue
            return False
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False


# Singleton instance
gemini_service = GeminiService()
