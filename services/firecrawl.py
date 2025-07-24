from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import logging
from typing import Dict, Any, Optional

load_dotenv()

class ZillowScrapingService:
    def __init__(self):
        self.app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        print("FIRECRAWL_API_KEY", os.getenv("FIRECRAWL_API_KEY"))
        self.logger = logging.getLogger(__name__)
    
    # https://docs.firecrawl.dev/features/stealth-mode
    async def scrape_zillow_property(self, zillow_url: str) -> Dict[str, Any]:
        """Scrape Zillow property with automatic zpid search"""
        
        # Check if URL already has zpid
        if "_zpid" not in zillow_url:
            self.logger.info(f"URL missing zpid, performing search simulation for: {zillow_url}")
            address = self._extract_address_from_url(zillow_url)
            return await self._search_and_scrape_zillow(address)
        
        # If URL has zpid, scrape directly
        return await self._scrape_zillow_direct(zillow_url)

    async def _search_and_scrape_zillow(self, address: str) -> Dict[str, Any]:
        """Use multiple approaches to search for property on Zillow"""
        
        try:
            self.logger.info(f"Starting comprehensive Zillow search for: {address}")
            
            # Try multiple approaches
            response = None
            
            # Approach 1: Simulated search with actions
            self.logger.info("Attempting approach 1: Simulated search with actions")
            response = await self._attempt_zillow_search_primary(address)
            
            if not response or not response.success:
                self.logger.info("Approach 1 failed, trying approach 2: Fallback selectors")
                # Approach 2: Fallback selectors
                response = await self._attempt_zillow_search_fallback(address)
            
            if not response or not response.success:
                self.logger.info("Approach 2 failed, trying approach 3: Direct search URL")
                # Approach 3: Direct search URL
                response = await self._attempt_zillow_search_direct_url(address)
            
            if not response or not response.success:
                self.logger.error(f"All search approaches failed for: {address}")
                raise Exception(f"Failed to search for property using all methods")
            
            # Get the final URL after search and redirect
            final_url = response.metadata.get("sourceURL") if response.metadata else "https://www.zillow.com/"
            self.logger.info(f"Search completed successfully, final URL: {final_url}")
            
            # Debug: Log some content to see what we got
            if response.markdown:
                self.logger.info(f"Response contains {len(response.markdown)} characters of markdown")
                # Log first 200 characters to see what we got
                self.logger.info(f"Response preview: {response.markdown[:200]}...")
            
            # Check if we ended up on a property page
            if "homedetails" in final_url and "_zpid" in final_url:
                self.logger.info("Success: Found direct property page")
                property_data = self._extract_zillow_data(response)
                return {
                    "success": True,
                    "url": final_url,
                    "final_url": final_url,
                    "property_data": property_data,
                    "raw_content": response.markdown or "",
                    "search_performed": True
                }
            
            elif any(keyword in final_url.lower() for keyword in ["homes", "search", "results"]):
                self.logger.info("Found search results page, extracting property links")
                # We're on search results page, try to find the first property link
                return await self._handle_search_results(response, address)
            
            else:
                # Try extracting property data directly from whatever page we got
                self.logger.warning(f"Unexpected final URL: {final_url}, attempting to extract data anyway")
                property_data = self._extract_zillow_data(response)
                
                # Check if we actually found property data
                if any(property_data.values()):  # If any field has data
                    return {
                        "success": True,
                        "url": final_url,
                        "final_url": final_url,
                        "property_data": property_data,
                        "raw_content": response.markdown or "",
                        "search_performed": True,
                        "note": "Data extracted from unexpected page"
                    }
                else:
                    raise Exception(f"Search did not lead to property data. Final URL: {final_url}")
                
        except Exception as e:
            self.logger.error(f"Search and scrape failed for {address}: {str(e)}")
            raise Exception(f"Property search failed: {str(e)}")
    
    async def _attempt_zillow_search_primary(self, address: str):
        """Primary search method using data-testid selectors with debugging"""
        try:
            self.logger.info(f"Starting primary search for: {address}")
            
            # Use actions to navigate and search with detailed debugging
            response = self.app.scrape_url(
                "https://www.zillow.com/",
                formats=["markdown", "html"],
                onlyMainContent=False,  # Get full page for debugging
                waitFor=3000,
                actions=[
                    {
                        "type": "wait",
                        "milliseconds": 4000  # Wait longer for page to fully load
                    },
                    {
                        "type": "screenshot",
                        "fullPage": False  # Take screenshot to see current state
                    },
                    {
                        "type": "click",
                        "selector": "div[data-testid='search-bar-container'] input[type='text']"
                    },
                    {
                        "type": "wait",
                        "milliseconds": 1000
                    },
                    {
                        "type": "write", 
                        "text": address
                    },
                    {
                        "type": "wait",
                        "milliseconds": 2000  # Wait longer for autocomplete
                    },
                    {
                        "type": "screenshot",
                        "fullPage": False  # Screenshot after typing
                    },
                    {
                        "type": "click",
                        "selector": "div[data-testid='search-bar-container'] button[type='submit']"
                    },
                    {
                        "type": "wait",
                        "milliseconds": 8000  # Wait longer for search results
                    },
                    {
                        "type": "screenshot",
                        "fullPage": False  # Screenshot of final result
                    }
                ],
                maxAge=0,  # Don't cache search results
                proxy="stealth",  # Use stealth mode for Zillow search
                timeout=60000  # Longer timeout
            )
            
            self.logger.info(f"Primary search response success: {response.success if response else 'No response'}")
            if response and response.metadata:
                self.logger.info(f"Primary search final URL: {response.metadata.get('sourceURL', 'No URL')}")
            
            return response
        except Exception as e:
            self.logger.error(f"Primary search method failed: {str(e)}")
            return None

    async def _attempt_zillow_search_fallback(self, address: str):
        """Fallback search method using alternative selectors"""
        try:
            self.logger.info(f"Starting fallback search for: {address}")
            
            response = self.app.scrape_url(
                "https://www.zillow.com/",
                formats=["markdown", "html"],
                onlyMainContent=True,
                waitFor=3000,
                actions=[
                    {
                        "type": "wait",
                        "milliseconds": 4000
                    },
                    {
                        "type": "click",
                        "selector": "input[placeholder*='Enter an address']"
                    },
                    {
                        "type": "wait",
                        "milliseconds": 1000
                    },
                    {
                        "type": "write", 
                        "text": address
                    },
                    {
                        "type": "wait",
                        "milliseconds": 2000
                    },
                    {
                        "type": "press",
                        "key": "Enter"  # Try pressing Enter instead of clicking submit
                    },
                    {
                        "type": "wait",
                        "milliseconds": 8000
                    }
                ],
                maxAge=0,
                proxy="stealth"
            )
            
            self.logger.info(f"Fallback search response success: {response.success if response else 'No response'}")
            if response and response.metadata:
                self.logger.info(f"Fallback search final URL: {response.metadata.get('sourceURL', 'No URL')}")
            
            return response
        except Exception as e:
            self.logger.error(f"Fallback search method failed: {str(e)}")
            return None

    async def _attempt_zillow_search_direct_url(self, address: str):
        """Third approach: Use direct search URL"""
        try:
            self.logger.info(f"Starting direct URL search for: {address}")
            
            # Format address for Zillow search URL
            search_query = address.replace(" ", "%20").replace(",", "%2C")
            search_url = f"https://www.zillow.com/homes/{search_query}_rb/"
            
            self.logger.info(f"Trying direct search URL: {search_url}")
            
            response = self.app.scrape_url(
                search_url,
                formats=["markdown", "html"],
                onlyMainContent=True,
                waitFor=5000,
                maxAge=0,
                proxy="stealth"
            )
            
            self.logger.info(f"Direct URL search response success: {response.success if response else 'No response'}")
            if response and response.metadata:
                self.logger.info(f"Direct URL search final URL: {response.metadata.get('sourceURL', 'No URL')}")
            
            return response
        except Exception as e:
            self.logger.error(f"Direct URL search method failed: {str(e)}")
            return None

    async def _handle_search_results(self, search_response, address: str) -> Dict[str, Any]:
        """Handle case where search leads to results page instead of direct property page"""
        
        try:
            # Extract the first property link from search results
            html_content = search_response.html or ""
            markdown_content = search_response.markdown or ""
            
            # Look for property links in the HTML
            import re
            property_link_pattern = r'href="([^"]*homedetails[^"]*_zpid[^"]*)"'
            matches = re.findall(property_link_pattern, html_content)
            
            if not matches:
                # Try alternative pattern
                property_link_pattern = r'"(\/homedetails\/[^"]*_zpid[^"]*)"'
                matches = re.findall(property_link_pattern, html_content)
            
            self.logger.info(f"Found {len(matches)} property links in search results")
            
            if matches:
                # Get the first property link and make it absolute
                first_property_url = matches[0]
                if first_property_url.startswith('/'):
                    first_property_url = f"https://www.zillow.com{first_property_url}"
                
                self.logger.info(f"Found property URL in search results: {first_property_url}")
                
                # Now scrape this specific property page
                return await self._scrape_zillow_direct(first_property_url)
            
            else:
                # Try to extract property data directly from search results
                self.logger.warning("No property links found, extracting from search results page")
                property_data = self._extract_zillow_data(search_response)
                
                return {
                    "success": True,
                    "url": search_response.metadata.get("sourceURL", ""),
                    "final_url": search_response.metadata.get("sourceURL", ""),
                    "property_data": property_data,
                    "raw_content": markdown_content,
                    "search_performed": True,
                    "note": "Data extracted from search results page"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to handle search results: {str(e)}")
            raise Exception(f"Could not process search results: {str(e)}")

    async def _scrape_zillow_direct(self, zillow_url: str) -> Dict[str, Any]:
        """Directly scrape a Zillow property URL (with zpid)"""
        
        try:
            # First try with basic scraping
            self.logger.info(f"Attempting direct scraping for: {zillow_url}")
            response = self.app.scrape_url(
                zillow_url,
                formats=["markdown", "html"],
                onlyMainContent=True,
                waitFor=2000,
                maxAge=604800000  # 1 week cache
            )

            # Check if the response was successful
            if not response.success:
                self.logger.info(f"Basic scraping failed, retrying with stealth proxy. Error: {getattr(response, 'error', 'Unknown error')}")
                # Retry with stealth proxy
                response = self.app.scrape_url(
                    zillow_url,
                    formats=["markdown", "html"],
                    onlyMainContent=True,
                    waitFor=2000,
                    proxy="stealth",  # Enable stealth mode
                    maxAge=604800000  # 1 week cache
                )
                
                if not response.success:
                    raise Exception(f"Stealth scraping also failed: {getattr(response, 'error', 'Unknown error')}")
             
            # Check status code in metadata if available
            status_code = response.metadata.get("statusCode") if response.metadata else None
            if status_code in [401, 403, 500]:
                self.logger.info(f"Got status code {status_code}, retrying with stealth proxy")
                # Retry with stealth proxy
                response = self.app.scrape_url(
                    zillow_url,
                    formats=["markdown", "html"], 
                    onlyMainContent=True,
                    waitFor=2000,
                    proxy="stealth",
                    maxAge=604800000  # 1 week
                )
                
                if not response.success:
                    raise Exception(f"Stealth retry failed: {getattr(response, 'error', 'Unknown error')}")
            
            # Extract property data from the scraped content
            property_data = self._extract_zillow_data(response)
            final_url = response.metadata.get("sourceURL", zillow_url) if response.metadata else zillow_url

            return {
                "success": True,
                "url": zillow_url,
                "final_url": final_url,
                "property_data": property_data,
                "raw_content": response.markdown or ""
            }
            
        except Exception as e:
            self.logger.error(f"Direct scraping failed for {zillow_url}: {str(e)}")
            
            # Fallback to stealth proxy on any exception
            try:
                self.logger.info("Retrying with stealth proxy")
                response = self.app.scrape_url(
                    zillow_url,
                    formats=["markdown", "html"],
                    onlyMainContent=True,
                    waitFor=2000,
                    proxy="stealth",
                    maxAge=604800000
                )
                
                if not response.success:
                    raise Exception(f"Stealth fallback failed: {getattr(response, 'error', 'Unknown error')}")
                
                property_data = self._extract_zillow_data(response)
                final_url = response.metadata.get("sourceURL", zillow_url) if response.metadata else zillow_url

                return {
                    "success": True,
                    "url": zillow_url,
                    "final_url": final_url,
                    "property_data": property_data,
                    "raw_content": response.markdown or ""
                }
                
            except Exception as stealth_error:
                self.logger.error(f"Stealth proxy also failed: {str(stealth_error)}")
                raise Exception(f"Both basic and stealth scraping failed: {str(stealth_error)}")
    
    def _extract_address_from_url(self, url: str) -> str:
        """Extract address from constructed Zillow URL for search"""
        import re

        # Handle the new format: /homedetails/address-city-state-zip
        pattern = r'/homedetails/([^/]+)'
        match = re.search(pattern, url)

        if match:
            # Convert hyphens back to spaces and format properly
            address_part = match.group(1)

            # Split and reconstruct the address
            parts = address_part.split("-")
            if len(parts) >= 4:
                # Reconstruct as "address, city, state zip"
                # Join all parts except last 2 as address, then city, state, zip
                state = parts[-2] if len(parts) >= 2 else ""
                zip_code = parts[-1] if len(parts) >= 1 else ""
                city = parts[-3] if len(parts) >= 3 else ""
                address = ' '.join(parts[:-3]) if len(parts) > 3 else ""
                
                return f"{address}, {city}, {state} {zip_code}".strip()
            else:
                # Fallback: just replace hyphens with spaces
                return address_part.replace('-', ' ')
        
        # If no match, assume it's already a properly formatted address
        return url.replace('https://www.zillow.com/homedetails/', '').replace('/', '')
    
    def _extract_zillow_data(self, response) -> Dict[str, Any]:
        """Extract structured data from FireCrawl response"""
        markdown = response.markdown or ""
        metadata = response.metadata or {}
        
        return {
            "address": metadata.get("title", "").replace(" | Zillow", ""),
            "price": self._extract_price(markdown),
            "bedrooms": self._extract_bedrooms(markdown),
            "bathrooms": self._extract_bathrooms(markdown),
            "square_feet": self._extract_square_feet(markdown),
            "lot_size": self._extract_lot_size(markdown),
            "year_built": self._extract_year_built(markdown),
            "property_type": self._extract_property_type(markdown),
            "description": metadata.get("description", ""),
            "images": metadata.get("ogImage", [])
        }
    
    def _extract_price(self, markdown: str) -> Optional[str]:
        """Extract property price from markdown content"""
        import re
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        match = re.search(price_pattern, markdown)
        return match.group(0) if match else None
    
    def _extract_bedrooms(self, markdown: str) -> Optional[int]:
        """Extract bedroom count"""
        import re
        bed_pattern = r'(\d+)\s*(?:bd|bed|bedroom)'
        match = re.search(bed_pattern, markdown.lower())
        return int(match.group(1)) if match else None
    
    def _extract_bathrooms(self, markdown: str) -> Optional[float]:
        """Extract bathroom count"""
        import re
        bath_pattern = r'(\d+(?:\.\d+)?)\s*(?:ba|bath|bathroom)'
        match = re.search(bath_pattern, markdown.lower())
        return float(match.group(1)) if match else None
    
    def _extract_square_feet(self, markdown: str) -> Optional[int]:
        """Extract square footage"""
        import re
        sqft_pattern = r'([\d,]+)\s*(?:sq ft|sqft|square feet)'
        match = re.search(sqft_pattern, markdown.lower())
        return int(match.group(1).replace(',', '')) if match else None
    
    def _extract_lot_size(self, markdown: str) -> Optional[str]:
        """Extract lot size"""
        import re
        lot_pattern = r'([\d,.]+)\s*(?:acres?|sq ft lot)'
        match = re.search(lot_pattern, markdown.lower())
        return match.group(0) if match else None
    
    def _extract_year_built(self, markdown: str) -> Optional[int]:
        """Extract year built"""
        import re
        year_pattern = r'(?:built|year built).*?(\d{4})'
        match = re.search(year_pattern, markdown.lower())
        return int(match.group(1)) if match else None
    
    def _extract_property_type(self, markdown: str) -> Optional[str]:
        """Extract property type"""
        types = ['single family', 'condo', 'townhouse', 'multi-family', 'land', 'mobile']
        markdown_lower = markdown.lower()
        for prop_type in types:
            if prop_type in markdown_lower:
                return prop_type.title()
        return None