"""
JobForge — LinkedIn Scraper (Stub)
LinkedIn actively blocks scraping. This is a stub that returns an empty list.
Use the manual "Paste JD" feature for LinkedIn jobs.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def scrape_linkedin(
    keywords: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Stub scraper for LinkedIn.
    LinkedIn blocks automated scraping — use manual JD paste instead.
    """
    logger.info("[LinkedIn] Stub scraper — LinkedIn scraping not available. Use 'Paste JD' for LinkedIn jobs.")
    return []
