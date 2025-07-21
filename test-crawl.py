from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

print("Testing FireCrawl response structure...")

try:
    # Test with a simple URL
    response = app.scrape_url("https://example.com", formats=["markdown"])
    
    print(f"Response type: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    
    # Try accessing common attributes
    if hasattr(response, 'success'):
        print(f"Success: {response.success}")
    
    if hasattr(response, 'data'):
        print(f"Data type: {type(response.data)}")
        print(f"Data: {response.data}")
    
    if hasattr(response, 'markdown'):
        print(f"Markdown: {response.markdown[:100]}...")
    
    if hasattr(response, 'metadata'):
        print(f"Metadata: {response.metadata}")
        
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")