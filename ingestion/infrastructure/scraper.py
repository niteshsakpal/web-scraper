import logging
import re
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    raw_html: str
    cleaned_text: str
    detected_language: str


class PlaywrightScraperService:
    def __init__(self, timeout_ms: int = 45000, respect_robots: bool = False) -> None:
        self.timeout_ms = timeout_ms
        self.respect_robots = respect_robots

    def scrape_url(self, url: str) -> ScrapeResult:
        if self.respect_robots and not self._is_allowed_by_robots(url):
            raise ValueError(f"Crawling blocked by robots.txt for URL: {url}")

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
                html = page.content()
                lang = page.evaluate("document.documentElement.lang || 'unknown'")
                browser.close()
        except PlaywrightTimeoutError as exc:
            logger.error("scrape.timeout", extra={"error": str(exc)})
            raise

        cleaned_text = self._extract_text(html)
        return ScrapeResult(raw_html=html, cleaned_text=cleaned_text, detected_language=lang)

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "form"]):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.body or soup
        text = main.get_text(separator="\n", strip=True)
        return re.sub(r"\n{2,}", "\n\n", text).strip()

    def _is_allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.read()
        return parser.can_fetch("RegulatoryIngestionBot", url)
