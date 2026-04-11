"""
JobForge — Lever Scraper
Fetches jobs from Lever public JSON API (no auth required).
"""

import httpx
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# DS/ML/AI title keywords for filtering
TITLE_KEYWORDS = [
    "data", "machine learning", "ml", "ai", "artificial intelligence",
    "deep learning", "nlp", "natural language", "computer vision",
    "research", "scientist", "analytics", "llm", "generative",
    "model", "mlops", "data engineer", "intern"
]

# Pre-configured company slugs
DEFAULT_COMPANIES = [
    "openai", "mistral", "together-ai", "modal",
    "replicate", "langchain", "llamaindex"
]


def _matches_keywords(title: str) -> bool:
    """Check if job title contains any DS/ML/AI keywords."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in TITLE_KEYWORDS)


def _classify_domain(title: str) -> str:
    """Classify job domain from title."""
    title_lower = title.lower()
    if "nlp" in title_lower or "natural language" in title_lower or "llm" in title_lower:
        return "NLP Engineer"
    elif "research" in title_lower:
        return "AI Research"
    elif "mlops" in title_lower or "ml ops" in title_lower or "platform" in title_lower:
        return "MLOps"
    elif "machine learning" in title_lower or "ml " in title_lower:
        return "ML Engineer"
    elif "data scientist" in title_lower or "data science" in title_lower:
        return "Data Science"
    elif "data analyst" in title_lower or "analytics" in title_lower:
        return "Data Analyst"
    elif "data engineer" in title_lower:
        return "Data Engineer"
    elif "computer vision" in title_lower or "cv " in title_lower:
        return "Computer Vision"
    elif "deep learning" in title_lower:
        return "Deep Learning"
    elif "intern" in title_lower:
        return "Intern"
    elif "ai" in title_lower or "artificial" in title_lower:
        return "AI Engineer"
    else:
        return "Data Science"


async def scrape_lever(
    companies: List[str] = None,
    keywords: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Scrape jobs from Lever public API.
    Returns list of job dicts ready for DB insertion.
    """
    companies = companies or DEFAULT_COMPANIES
    all_jobs = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for slug in companies:
            try:
                url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
                logger.info(f"[Lever] Fetching {slug}...")
                response = await client.get(url)

                if response.status_code == 404:
                    logger.warning(f"[Lever] Company '{slug}' not found (404)")
                    continue
                elif response.status_code != 200:
                    logger.warning(f"[Lever] {slug} returned status {response.status_code}")
                    continue

                postings = response.json()
                if not isinstance(postings, list):
                    logger.warning(f"[Lever] Unexpected response format from {slug}")
                    continue

                for posting in postings:
                    title = posting.get("text", "")
                    if not _matches_keywords(title):
                        continue

                    # Extract categories
                    categories = posting.get("categories", {})
                    location = categories.get("location", "Remote")
                    team = categories.get("team", "")
                    commitment = categories.get("commitment", "Full-time")

                    # Extract JD from description (can be HTML or plain text)
                    jd_parts = []
                    description = posting.get("descriptionPlain", "")
                    if description:
                        jd_parts.append(description)

                    # Also grab lists (requirements, responsibilities, etc.)
                    for lst in posting.get("lists", []):
                        list_title = lst.get("text", "")
                        if list_title:
                            jd_parts.append(f"\n{list_title}:")
                        for item in lst.get("content", "").split("<li>"):
                            cleaned = _clean_html_simple(item).strip()
                            if cleaned:
                                jd_parts.append(f"  - {cleaned}")

                    # Additional content
                    additional = posting.get("additional", "")
                    if additional:
                        jd_parts.append(_clean_html_simple(additional))

                    jd_raw = "\n".join(jd_parts)

                    # Parse date
                    posted_at = None
                    created_at_ms = posting.get("createdAt")
                    if created_at_ms:
                        try:
                            posted_at = datetime.fromtimestamp(created_at_ms / 1000)
                        except (ValueError, TypeError, OSError):
                            pass

                    all_jobs.append({
                        "title": title,
                        "company": slug.replace("-", " ").title(),
                        "location": location,
                        "job_type": commitment or "Full-time",
                        "domain": _classify_domain(title),
                        "source": "Lever",
                        "source_url": posting.get("hostedUrl", f"https://jobs.lever.co/{slug}/{posting.get('id', '')}"),
                        "jd_raw": jd_raw,
                        "posted_at": posted_at,
                        "scraped_at": datetime.utcnow(),
                    })

                logger.info(f"[Lever] Found matching jobs from {slug}")

            except httpx.TimeoutException:
                logger.error(f"[Lever] Timeout fetching {slug}")
            except Exception as e:
                logger.error(f"[Lever] Error fetching {slug}: {e}")

    logger.info(f"[Lever] Total jobs found: {len(all_jobs)}")
    return all_jobs


def _clean_html_simple(text: str) -> str:
    """Basic HTML tag removal."""
    if not text:
        return ""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    return text.strip()
