from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List, Optional, Any

class PageData(BaseModel):
    """Extracted data from a webpage."""
    title: Optional[str] = None
    meta_description: Optional[str] = None
    headings: Dict[str, List[str]] = Field(default_factory=dict)
    image_url: Optional[str] = None

class AuditRequest(BaseModel):
    """Request schema for auditing a URL."""
    url: HttpUrl

class AuditResponse(BaseModel):
    """Response schema containing audit results."""
    page_data: PageData
    json_ld: Dict[str, Any]
