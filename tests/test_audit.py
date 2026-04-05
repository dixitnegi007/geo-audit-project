import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Verify API is online."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_audit_invalid_url():
    """Verify validation for malformed URLs."""
    response = client.post("/audit", json={"url": "not-a-url"})
    assert response.status_code == 422

def test_audit_example_domain():
    """Verify audit logic with a real domain."""
    # Note: Requires internet access or mocking
    target_url = "https://example.com"
    response = client.post("/audit", json={"url": target_url})
    
    assert response.status_code == 200
    data = response.json()
    
    # Check Page Data
    assert "page_data" in data
    assert "title" in data["page_data"]
    assert "headings" in data["page_data"]
    
    # Check JSON-LD
    assert "json_ld" in data
    assert data["json_ld"]["@context"] == "https://schema.org"
    # Canonicalize URL comparison (ignore trailing slashes)
    assert data["json_ld"]["url"].rstrip("/") == target_url.rstrip("/")
