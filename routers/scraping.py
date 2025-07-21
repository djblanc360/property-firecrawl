from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from services.firecrawl import ZillowScrapingService
import logging
from datetime import datetime

router = APIRouter()
scraper = ZillowScrapingService()
logger = logging.getLogger(__name__)

class ZillowScrapeRequest(BaseModel):
    address: str
    city: str
    state: str
    zip: str

class ZillowScrapeResponse(BaseModel):
    success: bool
    url: str
    property_data: dict
    timestamp: str = None

def build_zillow_search_url(address: str, city: str, state: str, zip_code: str) -> str:
    # Format address for URL: replace spaces with hyphens, handle special characters
    formatted_address = address.replace(" ", "-").replace(",", "")
    formatted_city = city.replace(" ", "-")
    
    # Build search URL that will redirect to the property page
    search_url = f"https://www.zillow.com/homedetails/{formatted_address}-{formatted_city}-{state}-{zip_code}"
    return search_url

@router.post("/zillow", response_model=ZillowScrapeResponse)
async def scrape_zillow_property(request: ZillowScrapeRequest):
    # Scrape a Zillow property page using FireCrawl stealth mode
    zillow_url = build_zillow_search_url(request.address, request.city, request.state, request.zip)

    try:
        zillow_url = build_zillow_search_url(
            request.address, 
            request.city, 
            request.state, 
            request.zip
        )
        
        logger.info(f"Attempting to scrape: {zillow_url}") 

        result = await scraper.scrape_zillow_property(zillow_url)

        return ZillowScrapeResponse(
            success=result["success"],
            url=result.get("final_url", zillow_url),
            property_data=result["property_data"],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Zillow scraping failed for {request.address}, {request.city}, {request.state} {request.zip}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/zillow/batch")
async def scrape_multiple_zillow_properties(urls: list[HttpUrl]):
    # Scrape multiple Zillow properties (with rate limiting)
    results = []
    
    # Limit to 3 properties per request to avoid overwhelming the service
    properties_to_process = request.properties[:3]
    
    for prop_request in properties_to_process:
        try:
            # Build URL for this property
            zillow_url = build_zillow_search_url(
                prop_request.address,
                prop_request.city, 
                prop_request.state,
                prop_request.zip
            )
            
            result = await scraper.scrape_zillow_property(zillow_url)
            results.append({
                "success": result["success"],
                "address": f"{prop_request.address}, {prop_request.city}, {prop_request.state} {prop_request.zip}",
                "url": result.get("final_url", zillow_url),
                "property_data": result["property_data"]
            })
            
        except Exception as e:
            results.append({
                "success": False,
                "address": f"{prop_request.address}, {prop_request.city}, {prop_request.state} {prop_request.zip}",
                "url": None,
                "error": str(e)
            })
    
    return {"results": results}

@router.post("/zillow/url")
async def scrape_zillow_by_url(zillow_url: str):
    # Scrape using a direct Zillow URL (fallback method)
    
    # validate Zillow URL
    if "zillow.com" not in zillow_url:
        raise HTTPException(
            status_code=400, 
            detail="URL must be a Zillow URL"
        )
    
    try:
        result = await scraper.scrape_zillow_property(zillow_url)
        return {
            "success": result["success"],
            "url": result["url"],
            "property_data": result["property_data"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Zillow URL scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))