import json
import logging
from openai import OpenAI
from app.models import PageData
from app.config import settings
from typing import Any, Dict

logger = logging.getLogger("geo-audit.generator")

class JSONLDGenerator:
    """
    Intelligent JSON-LD generation service.
    Uses AI if a valid OpenAI key is provided, otherwise falls back to a rule-based engine.
    """
    def __init__(self):
        # Only initialize OpenAI if key is present and not empty
        api_key = settings.OPENAI_API_KEY
        if api_key and api_key.strip() and not api_key.startswith("your_"):
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
            logger.info("Using rule-based generation (OpenAI key not configured).")

    def generate(self, page_data: PageData, url: str) -> Dict[str, Any]:
        if self.client:
            return self._generate_with_llm(page_data, url)
        return self._generate_rule_based(page_data, url)

    def _generate_with_llm(self, page_data: PageData, url: str) -> Dict[str, Any]:
        prompt = f"""
        Webpage Audit Data:
        URL: {url}
        Title: {page_data.title or "N/A"}
        Description: {page_data.meta_description or "N/A"}
        Headings: {json.dumps(page_data.headings)}
        Image: {page_data.image_url or "N/A"}
        
        Task: Create a JSON-LD object (Article, Product, or Organization). Return ONLY valid JSON.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.choices[0].message.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            logger.warning(f"LLM generation failed, falling back to rules: {e}")
            return self._generate_rule_based(page_data, url)

    def _generate_rule_based(self, page_data: PageData, url: str) -> Dict[str, Any]:
        # Rule-based decision engine
        text_blob = f"{page_data.title or ''} {page_data.meta_description or ''} ".lower()
        headings_blob = " ".join([h for h_list in page_data.headings.values() for h in h_list]).lower()
        full_content = text_blob + headings_blob
        
        schema_type = "WebPage"
        if any(k in full_content for k in ["buy", "price", "shop", "product", "sku"]):
            schema_type = "Product"
        elif any(k in full_content for k in ["blog", "news", "post", "article", "author"]):
            schema_type = "Article"
        elif any(k in full_content for k in ["company", "about", "team", "contact", "official"]):
            schema_type = "Organization"

        return {
            "@context": "https://schema.org",
            "@type": schema_type,
            "url": url,
            "name": page_data.title or "Untitled Page",
            "description": page_data.meta_description or "GEO optimized content audit.",
            "image": page_data.image_url
        }
