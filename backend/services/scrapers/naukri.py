"""
JobForge — Naukri Scraper (Stub)
Naukri has aggressive anti-bot protection. This is a stub.
Use the manual "Paste JD" feature for Naukri jobs.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def scrape_naukri(
    keywords: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Stub scraper for Naukri.
    Naukri has Cloudflare protection — use manual JD paste instead.
    """
    logger.info("[Naukri] Stub scraper — Naukri scraping not available. Use 'Paste JD' for Naukri jobs.")
    return []
