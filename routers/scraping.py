from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from services.scraper import ZillowScrapingService
import logging

router = APIRouter()
scraper = ZillowScrapingService()
logger = logging.getLogger(__name__)

class ZillowScrapeRequest(BaseModel):
    zillow_url: HttpUrl

class ZillowScrapeResponse(BaseModel):
    success: bool
    url: str
    property_data: dict
    timestamp: str = None

@router.post("/zillow", response_model=ZillowScrapeResponse)
async def scrape_zillow_property(request: ZillowScrapeRequest):
    """Scrape a Zillow property page using FireCrawl stealth mode"""
    
    # Validate Zillow URL
    if "zillow.com/homedetails/" not in str(request.zillow_url):
        raise HTTPException(
            status_code=400, 
            detail="URL must be a Zillow property page (zillow.com/homedetails/)"
        )
    
    try:
        result = await scraper.scrape_zillow_property(str(request.zillow_url))
        return ZillowScrapeResponse(
            success=result["success"],
            url=result["url"],
            property_data=result["property_data"],
            timestamp=str(datetime.utcnow())
        )
    except Exception as e:
        logger.error(f"Zillow scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zillow/batch")
async def scrape_multiple_zillow_properties(urls: list[HttpUrl]):
    """Scrape multiple Zillow properties (with rate limiting)"""
    results = []
    
    for url in urls[:3]:  # Limit to 3 properties per request
        try:
            result = await scraper.scrape_zillow_property(str(url))
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "url": str(url),
                "error": str(e)
            })
    
    return {"results": results}
