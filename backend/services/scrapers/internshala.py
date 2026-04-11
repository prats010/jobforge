"""
JobForge — Internshala Scraper (Best-effort)
Attempts to scrape internship listings from Internshala.
May break if site structure changes.
"""

import httpx
import logging
import re
from typing import List, Dict, Any
from datetime import datetime
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

TITLE_KEYWORDS = [
    "data", "machine learning", "ml", "ai", "artificial intelligence",
    "deep learning", "nlp", "python", "analytics", "research",
    "science", "computer vision", "intern"
]


def _get_random_headers() -> dict:
    """Generate request headers with random user agent."""
    try:
        ua = UserAgent()
        user_agent = ua.random
    except Exception:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


async def scrape_internshala(
    keywords: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Best-effort scrape of Internshala internship listings.
    Returns list of job dicts. May return empty if site blocks the request.
    """
    if keywords is None:
        keywords = ["data science", "machine learning", "artificial intelligence"]

    all_jobs = []

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for keyword in keywords:
            try:
                # Internshala URL format
                slug = keyword.lower().replace(" ", "-")
                url = f"https://internshala.com/internships/{slug}-internship"
                logger.info(f"[Internshala] Fetching: {url}")

                response = await client.get(url, headers=_get_random_headers())

                if response.status_code != 200:
                    logger.warning(f"[Internshala] Got status {response.status_code} for '{keyword}'")
                    continue

                # Parse HTML
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "lxml")
                except Exception:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")

                # Find internship cards
                cards = soup.select(".internship_meta") or soup.select(".individual_internship")
                if not cards:
                    # Try alternate selectors
                    cards = soup.select("[class*='internship']")

                for card in cards[:20]:  # Limit to 20 per keyword
                    try:
                        # Extract title
                        title_el = card.select_one(".profile a, h3 a, .job-title-href, .profile")
                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title:
                            continue

                        # Extract company
                        company_el = card.select_one(".company-name, .company_name, [class*='company']")
                        company = company_el.get_text(strip=True) if company_el else "Unknown"

                        # Extract location
                        location_el = card.select_one(".location_link, [id='location_names'], [class*='location']")
                        location = location_el.get_text(strip=True) if location_el else "India"

                        # Extract stipend
                        stipend_el = card.select_one(".stipend, [class*='stipend']")
                        stipend = stipend_el.get_text(strip=True) if stipend_el else None

                        # Extract link
                        link_el = card.select_one("a[href*='/internship/']")
                        link = ""
                        if link_el and link_el.get("href"):
                            href = link_el["href"]
                            if not href.startswith("http"):
                                href = f"https://internshala.com{href}"
                            link = href

                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_type": "Internship",
                            "domain": "Data Science",
                            "source": "Internshala",
                            "source_url": link,
                            "jd_raw": f"Internship: {title} at {company}. Location: {location}. Stipend: {stipend or 'Not specified'}",
                            "salary_range": stipend,
                            "posted_at": None,
                            "scraped_at": datetime.utcnow(),
                        })

                    except Exception as e:
                        logger.debug(f"[Internshala] Error parsing card: {e}")
                        continue

                logger.info(f"[Internshala] Found {len(all_jobs)} internships for '{keyword}'")

            except httpx.TimeoutException:
                logger.error(f"[Internshala] Timeout for '{keyword}'")
            except Exception as e:
                logger.error(f"[Internshala] Error scraping '{keyword}': {e}")

    return all_jobs
