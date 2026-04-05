import sys
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Standardized logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geo-audit")

# Fix path resolution for absolute imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Absolute imports
try:
    from app.models import AuditRequest, AuditResponse
    from app.scraper import Scraper
    from app.generator import JSONLDGenerator
except ImportError:
    from models import AuditRequest, AuditResponse
    from scraper import Scraper
    from generator import JSONLDGenerator

app = FastAPI(
    title="GEO Audit System",
    description="Villion Inc. Competency Assessment Prototype.",
    version="1.1.5"
)

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Services
scraper = Scraper()
generator = JSONLDGenerator()

@app.get("/")
async def serve_frontend():
    """Serves the Product-style interface."""
    return FileResponse("app/static/index.html")

@app.post("/audit", response_model=AuditResponse)
async def perform_audit(request: AuditRequest):
    url_str = str(request.url)
    logger.info(f"Audit request for: {url_str}")
    
    try:
        page_data = scraper.fetch_and_extract(url_str)
        json_ld = generator.generate(page_data, url_str)
        
        return AuditResponse(
            page_data=page_data,
            json_ld=json_ld
        )
    except Exception as e:
        logger.error(f"Audit Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
