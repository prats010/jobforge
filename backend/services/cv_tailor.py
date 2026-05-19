"""
JobForge — CV Tailoring Service
AI-powered resume tailoring logic.
"""

import re
import logging
from typing import Dict, Any, List
from services.groq_service import groq_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Post-processing: undo any markdown tables the AI created
# ---------------------------------------------------------------------------

def _find_original_lines_for_table(table_lines: List[str], original_resume: str) -> List[str]:
    """
    Given a markdown table block from the AI output, locate the matching
    plain-text lines from the original resume and return those instead.

    Strategy:
      1. Extract the first-column values of each data row in the table.
      2. Search the original resume for lines containing those values followed
         by a colon (i.e. "Domains: …", "Languages: …").
      3. Return those original lines; if none found, fall back to converting
         the table rows into "Key: value" plain text ourselves.
    """
    # Collect first-column values from non-separator table rows
    table_keys: List[str] = []
    for line in table_lines:
        stripped = line.strip()
        # Skip separator rows like |---|---|
        if re.match(r'^\|[-:\s|]+\|$', stripped):
            continue
        cells = [c.strip() for c in stripped.strip('|').split('|')]
        if cells and cells[0] and cells[0].lower() not in ('category', 'key', 'field'):
            table_keys.append(cells[0].lower())

    if not table_keys:
        return table_lines  # nothing to identify — leave unchanged

    # Find matching lines in the original resume
    original_lines = original_resume.splitlines()
    matched: List[str] = []
    for orig_line in original_lines:
        for key in table_keys:
            if key in orig_line.lower() and ':' in orig_line:
                matched.append(orig_line)
                break  # don't double-add the same line

    if matched:
        logger.info(
            f"Table post-processor: replaced {len(table_lines)}-row table "
            f"with {len(matched)} original line(s)."
        )
        return matched

    # Fallback: convert table rows to "Key: value" text
    fallback: List[str] = []
    for line in table_lines:
        stripped = line.strip()
        if re.match(r'^\|[-:\s|]+\|$', stripped):
            continue
        cells = [c.strip() for c in stripped.strip('|').split('|')]
        if len(cells) >= 2 and cells[0] and cells[0].lower() not in ('category', 'key', 'field'):
            fallback.append(f"{cells[0]}: {cells[1]}")

    logger.info(
        f"Table post-processor (fallback): converted {len(table_lines)}-row "
        f"table to {len(fallback)} plain-text line(s)."
    )
    return fallback if fallback else table_lines


def _fix_table_conversions(original_resume: str, tailored_resume: str) -> str:
    """
    Scan the AI-tailored resume for any markdown table blocks (lines that
    start with '|') and replace each block with the corresponding original
    plain-text lines from the source resume.

    This is a deterministic safeguard that runs *after* the AI returns its
    result, so it works regardless of whether the LLM followed the prompt.
    """
    tailored_lines = tailored_resume.splitlines()
    result_lines: List[str] = []
    i = 0

    while i < len(tailored_lines):
        line = tailored_lines[i]

        # Detect start of a markdown table block
        if re.match(r'^\s*\|', line):
            table_block: List[str] = []
            while i < len(tailored_lines) and re.match(r'^\s*\|', tailored_lines[i]):
                table_block.append(tailored_lines[i])
                i += 1

            replacement = _find_original_lines_for_table(table_block, original_resume)
            result_lines.extend(replacement)
        else:
            result_lines.append(line)
            i += 1

    fixed = '\n'.join(result_lines)
    if fixed != tailored_resume:
        logger.info("Table post-processor: tailored resume was modified to remove table(s).")
    return fixed


def _fix_blank_lines(tailored_resume: str) -> str:
    """
    Restore blank lines that the AI removed between resume entries.

    Rule: If a line starts with '**' (a bold entry — degree, job, project)
    and the immediately preceding line is non-empty AND is not itself a
    heading/bullet/bold-entry, insert a blank line before it.

    This reliably separates entries like:
        M.Sc. line
        Focus: ...
        B.Sc. line     ← blank line should be here
    """
    lines = tailored_resume.splitlines()
    result: List[str] = []

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Is this a bold-entry line (degree / job title / project name)?
        is_bold_entry = stripped.startswith('**') and not stripped.startswith('**Keywords')

        if is_bold_entry and idx > 0:
            prev = lines[idx - 1].strip()
            # Previous line is non-empty and isn't a heading, bullet, or blank already
            if prev and not prev.startswith(('#', '-', '*', '|', '##')):
                # Check that we haven't already appended a blank
                if result and result[-1].strip() != '':
                    result.append('')
                    logger.debug(f"Blank line inserted before: {stripped[:60]}")

        result.append(line)

    fixed = '\n'.join(result)
    if fixed != tailored_resume:
        logger.info("Blank-line post-processor: restored missing blank lines between entries.")
    return fixed


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def tailor_resume_for_job(resume: str, job_description: str, keywords: List[str] = None) -> Dict[str, Any]:
    """
    Tailor a resume for a specific job description using AI,
    then apply deterministic post-processing to guarantee structure fidelity.
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

        raw_tailored = result["tailored_resume_md"]

        # --- Post-process: restore any lines the AI converted to tables ---
        clean_tailored = _fix_table_conversions(resume, raw_tailored)

        # --- Post-process: restore blank lines between entries the AI collapsed ---
        clean_tailored = _fix_blank_lines(clean_tailored)

        return {
            "tailored_md": clean_tailored,
            "keywords_injected": result.get("keywords_injected", []),
            "changes_summary": result.get("changes_summary", "Resume tailored successfully."),
        }

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"CV tailoring failed: {e}")
        raise RuntimeError(f"AI CV tailoring failed: {e}")
