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
        prompt = f"""You are a precise resume editor. Your task is to make MINIMAL, SURGICAL edits to the resume below so it better matches the job description — while preserving its structure EXACTLY.

ABSOLUTE RULES — violating any of these is FORBIDDEN:
1. EXACT SAME LENGTH: Your output MUST contain the EXACT same number of lines and bullet points as the input resume. NOT A SINGLE LINE MORE. DO NOT ADD NEW CONTENT.
2. DO NOT EXPAND WORD COUNT: When injecting a keyword into a bullet point, you MUST keep the bullet point the same length or shorter than the original. Do not add long explanations that cause the sentence to wrap to a second line.
3. PRESERVE EVERY LINE: Every single line that exists in the original resume MUST appear in the output. Do not delete, skip, merge, or collapse any line.
4. PRESERVE ALL BLANK LINES: Keep empty lines exactly where they are. They are structural separators — do not remove them.
5. PRESERVE SECTION ORDER: Sections must appear in the exact same order as the original.
6. PRESERVE FORMATTING CHARACTERS: If a line starts with "-", "#", "##", "###", "*", or any other markdown symbol, keep that symbol. Do not change heading levels.
7. ONLY EDIT WITHIN LINES: You may rephrase or expand the content of an existing bullet point or sentence to naturally include a relevant keyword — but the line must still exist and serve the same purpose. DO NOT create a new bullet point to hold a keyword.
8. DO NOT ADD NEW SECTIONS: Do not create new section headers or new bullet points that didn't exist before.
7. DO NOT REORDER BULLETS: Bullet points within a section must stay in the same order.
8. MINIMAL CHANGES ONLY: Only touch lines where a keyword or relevant phrase can be naturally inserted. Leave all other lines WORD-FOR-WORD identical to the original.
9. SENTENCE CASE: Do not use all-caps for body text.
10. NEVER CREATE TABLES: Do NOT convert any lines into markdown tables (|---|---| format). If the original has "Category: item1, item2, item3" — keep it as exactly that plain-text format. Tables are strictly forbidden.
11. NEVER REMOVE LIST ITEMS: If a line contains a comma-separated list (e.g., "Python, SQL, JavaScript"), you may ADD items but must NEVER remove any existing items from the list.

HOW TO TAILOR (only do these):
- In existing bullet points, naturally weave in 1-2 relevant keywords from the job description if it makes sense contextually.
- Slightly rephrase an existing bullet to better match the job's language — but keep the same meaning and the same line.
- Update a skills line to include a relevant technology if it was missing.

Resume (treat every line as sacred — preserve all):
{resume}

Job Description:
{job_description}

Keywords to naturally inject where relevant:
{keywords_str}

Return ONLY valid JSON:
{{
    "tailored_resume_md": "<the full resume with EVERY original line present, only minimally edited>",
    "keywords_injected": ["list of keywords you actually added"],
    "changes_summary": "Brief description of what was changed and why"
}}"""
        return self._extract_json(self._call_with_retry(prompt))

    def structure_resume_text(self, raw_text: str) -> str:
        """
        Convert raw PDF-extracted text (which often has no line breaks or
        scrambled layout) into clean, properly formatted Markdown.

        This is called ONCE at upload time. The result is stored as the
        base resume so all downstream operations work with clean input.
        """
        prompt = f"""You are a resume formatting expert. The text below was extracted from a PDF using automated tools and may have lost its line breaks, merged columns into one line, or scrambled its layout.

Your task: Reconstruct the resume as clean, well-structured Markdown that faithfully preserves ALL original content.

RULES:
1. DO NOT invent, add, or remove any information — only reformat what is there.
2. THE PERSON'S NAME must be the very first line, formatted as "# Full Name" (a Markdown H1 heading).
3. CONTACT INFO (email, phone, LinkedIn, GitHub, Portfolio, location) goes on the line immediately after the name, items separated by " | ".
4. Use "## SECTION NAME" (H2) for all section headings: SUMMARY, EDUCATION, EXPERIENCE, PROJECTS, TECHNICAL SKILLS, CERTIFICATIONS, ACHIEVEMENTS.
5. Use "**Label**" bold for each degree, job title, and project name.
6. BLANK LINE BETWEEN ENTRIES: Every individual entry (each degree, each job, each project) MUST be separated from the next by a blank line. This is mandatory.
7. Use bullet points (-) for lists of responsibilities, achievements, or tools.
8. For skills, EVERY category MUST be on its own separate line like "**Category:** skill, skill". Never combine multiple categories on one line. NO markdown tables.
9. Preserve dates exactly as they appear in the source, typically in italics: *Month Year – Month Year*
10. Do NOT create markdown tables (|---|---|). Use plain text for everything.
11. Output ONLY the formatted resume — no preamble, no commentary, no code fences.

Example of EXACTLY the required output structure:
# John Doe
email@example.com | +1 234 567 8900 | linkedin.com/in/johndoe | github.com/johndoe | City, Country

## SUMMARY
Brief professional summary here.

## EDUCATION
**M.Sc. Degree Name — University Name, City**
*Month Year – Month Year (Expected)*
Focus: Subject A, Subject B

**B.Sc. Degree Name — Another University, City**
*Month Year – Month Year*
Coursework: Topic A, Topic B

## EXPERIENCE
**Job Title — Company Name**
*Month Year – Month Year*
- Responsibility one
- Responsibility two

**Earlier Job Title — Other Company**
*Month Year – Month Year*
- Responsibility one

## PROJECTS
**Project Name** | *Tech, Stack*
- What it does
- What you built

**Another Project** | *Tech, Stack*
- Description

## TECHNICAL SKILLS
**Domains:** Machine Learning, NLP
**Languages:** Python, JavaScript
**Tools:** React, FastAPI

Raw extracted text:
{raw_text}"""

        # Use plain text response (not JSON) for this call
        result = self._call_with_retry(prompt, is_json=False)
        structured = self._fix_resume_header(result.strip())
        structured = self._fix_entry_spacing(structured)
        return structured


    def _fix_entry_spacing(self, md: str) -> str:
        """
        Ensure a blank line exists before every bold entry line (**text**).
        This deterministically separates degree/job/project entries that the
        AI may have joined without a blank line.
        """
        lines = md.splitlines()
        result: list = []

        for idx, line in enumerate(lines):
            stripped = line.strip()
            is_bold_entry = (stripped.startswith('**')
                             and not stripped.startswith('**Key')
                             and not stripped.startswith('**Domain')
                             and not stripped.startswith('**Language')
                             and not stripped.startswith('**Tool'))

            if is_bold_entry and idx > 0:
                prev = lines[idx - 1].strip()
                # Insert blank if previous line has content and is not a heading/bullet
                if prev and not prev.startswith(('#', '-', '##')):
                    if result and result[-1].strip() != '':
                        result.append('')

            result.append(line)

        return '\n'.join(result)


    def _fix_resume_header(self, md: str) -> str:
        """
        Deterministic post-processor that runs after AI structuring.
        Guarantees:
          1. The person's name is on the first line as # Name (H1)
          2. Contact info is on its own line immediately after
          3. Section headings written in ALL CAPS plain text get promoted to ## H2
        """
        import re
        lines = md.splitlines()
        if not lines:
            return md

        result = []
        i = 0

        # ── Fix the header block (name + contact) ───────────────────────────
        # Find first non-empty line
        while i < len(lines) and not lines[i].strip():
            i += 1

        if i < len(lines):
            first = lines[i].strip()

            # Already an H1 — leave it alone
            if first.startswith('# '):
                result.append(lines[i])
                i += 1
            else:
                # The first line might be "Name | email | phone | ..."
                # or just the name alone
                if '|' in first:
                    parts = [p.strip() for p in first.split('|')]
                    # First chunk is the name, rest is contact info
                    name = parts[0].strip('*# ')   # strip any bold/heading chars
                    contact = ' | '.join(p for p in parts[1:] if p)
                    result.append(f'# {name}')
                    if contact:
                        result.append(contact)
                else:
                    # Single-word or full-name line with no pipe
                    result.append(f'# {first.strip("*# ")}')
                i += 1

        # ── Process the rest: promote bare ALL-CAPS section headings ────────
        # e.g. "SUMMARY", "**SUMMARY**", "EXPERIENCE" → ## SUMMARY
        caps_section = re.compile(
            r'^\*{0,2}(SUMMARY|EDUCATION|EXPERIENCE|PROJECTS?|TECHNICAL SKILLS?|SKILLS?|'
            r'CERTIFICATIONS?|ACHIEVEMENTS?|AWARDS?|PUBLICATIONS?|LANGUAGES?)\*{0,2}$',
            re.IGNORECASE,
        )

        for j in range(i, len(lines)):
            line = lines[j]
            stripped = line.strip()
            if caps_section.match(stripped):
                # Promote to ## heading if not already one
                clean = re.sub(r'^\*+|\*+$', '', stripped).strip()
                result.append(f'\n## {clean.upper()}')
            else:
                result.append(line)

        return '\n'.join(result)


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
