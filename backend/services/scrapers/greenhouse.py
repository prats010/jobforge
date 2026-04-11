"""
JobForge — Greenhouse Scraper
Fetches jobs from Greenhouse public JSON API (no auth required).
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
    "anthropic", "huggingface", "openai", "deepmind", "databricks",
    "cohere", "scale-ai", "wandb", "neptune-ai", "clarifai",
    "snorkel-ai", "weights-biases", "arize-ai", "labelbox"
]


def _matches_keywords(title: str) -> bool:
    """Check if job title contains any DS/ML/AI keywords."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in TITLE_KEYWORDS)


async def scrape_greenhouse(
    companies: List[str] = None,
    keywords: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Scrape jobs from Greenhouse public API.
    Returns list of job dicts ready for DB insertion.
    """
    companies = companies or DEFAULT_COMPANIES
    all_jobs = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for slug in companies:
            try:
                url = f"https://api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
                logger.info(f"[Greenhouse] Fetching {slug}...")
                response = await client.get(url)

                if response.status_code == 404:
                    logger.warning(f"[Greenhouse] Company '{slug}' not found (404)")
                    continue
                elif response.status_code != 200:
                    logger.warning(f"[Greenhouse] {slug} returned status {response.status_code}")
                    continue

                data = response.json()
                jobs = data.get("jobs", [])

                for job in jobs:
                    title = job.get("title", "")
                    if not _matches_keywords(title):
                        continue

                    # Extract location
                    location = "Remote"
                    if job.get("location", {}).get("name"):
                        location = job["location"]["name"]

                    # Extract JD from content (HTML)
                    jd_raw = job.get("content", "")

                    # Parse date
                    posted_at = None
                    if job.get("updated_at"):
                        try:
                            posted_at = datetime.fromisoformat(
                                job["updated_at"].replace("Z", "+00:00")
                            )
                        except (ValueError, TypeError):
                            pass

                    all_jobs.append({
                        "title": title,
                        "company": slug.replace("-", " ").title(),
                        "location": location,
                        "job_type": "Full-time",
                        "domain": _classify_domain(title),
                        "source": "Greenhouse",
                        "source_url": job.get("absolute_url", f"https://boards.greenhouse.io/{slug}/jobs/{job.get('id', '')}"),
                        "jd_raw": _clean_html(jd_raw),
                        "posted_at": posted_at,
                        "scraped_at": datetime.utcnow(),
                    })

                logger.info(f"[Greenhouse] Found {len([j for j in all_jobs if slug.replace('-', ' ').title() in j.get('company', '')])} matching jobs from {slug}")

            except httpx.TimeoutException:
                logger.error(f"[Greenhouse] Timeout fetching {slug}")
            except Exception as e:
                logger.error(f"[Greenhouse] Error fetching {slug}: {e}")

    logger.info(f"[Greenhouse] Total jobs found: {len(all_jobs)}")
    return all_jobs


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


def _clean_html(html_text: str) -> str:
    """Strip HTML tags for a cleaner JD text."""
    if not html_text:
        return ""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_text, "lxml")
        return soup.get_text(separator="\n", strip=True)
    except Exception:
        # Fallback: basic tag stripping
        import re
        return re.sub(r"<[^>]+>", "", html_text)
