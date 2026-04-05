import requests
import urllib3
import re
from bs4 import BeautifulSoup
from typing import Optional
from app.models import PageData
from urllib.parse import urljoin

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Scraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_and_extract(self, url: str) -> PageData:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return self._parse_html(response.text, url)
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch webpage: {str(e)}")

    def _parse_html(self, html: str, base_url: str) -> PageData:
        soup = BeautifulSoup(html, "html.parser")
        
        # CLEANUP: Remove only non-visible/technical tags
        for element in soup(["script", "style", "noscript", "iframe", "svg", "canvas"]):
            element.decompose()
        
        # 1. Title
        title = soup.title.get_text(strip=True) if soup.title else None
        
        # 2. Meta Description (Case-insensitive)
        desc_tag = (
            soup.find("meta", attrs={"name": re.compile(r'^description$', re.I)}) or 
            soup.find("meta", attrs={"property": re.compile(r'^og:description$', re.I)}) or
            soup.find("meta", attrs={"name": re.compile(r'^twitter:description$', re.I)})
        )
        meta_description = desc_tag.get("content", "").strip() if desc_tag else None
        
        # 3. Headings (Filter out empty strings)
        headings = {
            "h1": [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)],
            "h2": [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)],
            "h3": [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]
        }
        
        # 4. Image URL (Prioritize OG/Twitter Meta)
        image_url = None
        img_meta = (
            soup.find("meta", attrs={"property": re.compile(r'^og:image$', re.I)}) or
            soup.find("meta", attrs={"name": re.compile(r'^og:image$', re.I)}) or
            soup.find("meta", attrs={"name": re.compile(r'^twitter:image$', re.I)})
        )
        if img_meta:
            image_url = img_meta.get("content")
        
        # Fallback to first meaningful image
        if not image_url:
            img_tag = soup.find("img", src=True)
            if img_tag:
                image_url = urljoin(base_url, img_tag["src"])

        return PageData(
            title=title,
            meta_description=meta_description,
            headings=headings,
            image_url=image_url
        )
