from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import logging
from typing import Dict, Any

load_dotenv()

class ZillowScrapingService:
    def __init__(self):
        self.app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        print("FIRECRAWL_API_KEY", os.getenv("FIRECRAWL_API_KEY"))
        self.logger = logging.getLogger(__name__)
    
    # https://docs.firecrawl.dev/features/stealth-mode
    async def scrape_zillow_property(self, zillow_url: str) -> Dict[str, Any]:
        # Scrape Zillow property with automatic stealth fallback
        
        try:
            # First try with basic scraping
            content = self.app.scrape_url(
                zillow_url,
                params={
                    "formats": ["markdown", "html"],
                    "onlyMainContent": True,
                    "waitFor": 2000
                }
            )
            
            # Check if error status code
            status_code = content.get("metadata", {}).get("statusCode")
            if status_code in [401, 403, 500]:
                self.logger.info(f"Got status code {status_code}, retrying with stealth proxy")
                # Retry with stealth proxy
                content = self.app.scrape_url(
                    zillow_url,
                    params={
                        "formats": ["markdown", "html"], 
                        "onlyMainContent": True,
                        "waitFor": 2000,
                        "proxy": "stealth"  # Enable stealth mode
                    }
                )
            
            # Extract property data from the scraped content
            property_data = self._extract_zillow_data(content)
            final_url = content.get("metadata", {}).get("sourceURL", zillow_url)

            return {
                "success": True,
                "url": zillow_url,
                "final_url": final_url,
                "property_data": property_data,
                "raw_content": content.get("markdown", "")
            }
            
        except Exception as e:
            self.logger.error(f"Basic scraping failed for {zillow_url}: {str(e)}")
            
            # Fallback to stealth proxy on any exception
            try:
                self.logger.info("Retrying with stealth proxy")
                content = self.app.scrape_url(
                    zillow_url,
                    params={
                        "formats": ["markdown", "html"],
                        "onlyMainContent": True, 
                        "waitFor": 2000,
                        "proxy": "stealth"
                    }
                )
                
                property_data = self._extract_zillow_data(content)
                final_url = content.get("metadata", {}).get("sourceURL", zillow_url)

                return {
                    "success": True,
                    "url": zillow_url,
                    "final_url": final_url,
                    "property_data": property_data,
                    "raw_content": content.get("markdown", "")
                }
                
            except Exception as stealth_error:
                self.logger.error(f"Stealth proxy also failed: {str(stealth_error)}")
                raise Exception(f"Both basic and stealth scraping failed: {str(stealth_error)}")
    
    def _extract_zillow_data(self, content: Dict[str, Any]) -> Dict[str, Any]:
        # Extract structured data from FireCrawl response
        markdown = content.get("markdown", "")
        # metadata = content.get("metadata", {})
        # final_url = content.get("metadata", {}).get("sourceURL", "")
        
        return {
            # "address": metadata.get("title", "").replace(" | Zillow", ""),
            "price": self._extract_price(markdown),
            # "bedrooms": self._extract_bedrooms(markdown),
            # "bathrooms": self._extract_bathrooms(markdown),
            # "square_feet": self._extract_square_feet(markdown),
            # "final_url": final_url
        }
    
    # extraction methods...
    def _extract_price(self, markdown: str):
        import re
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        match = re.search(price_pattern, markdown)
        return match.group(0) if match else None
        