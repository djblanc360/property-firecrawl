#!/usr/bin/env python3
"""
Basic usage example for Property Firecrawl.

This example demonstrates how to use the PropertyCrawler class
to scrape property data from websites.
"""

import os
from property_firecrawl import PropertyCrawler, Config


def main():
    """Demonstrate basic usage of Property Firecrawl."""
    
    # Example URLs (replace with real property listing URLs)
    example_urls = [
        "https://example-property-site.com/listing/123",
        "https://example-property-site.com/listing/456", 
        "https://example-property-site.com/listing/789"
    ]
    
    print("Property Firecrawl - Basic Usage Example")
    print("=" * 40)
    
    # Check for API key
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ Error: FIRECRAWL_API_KEY environment variable not set")
        print("Please set your Firecrawl API key:")
        print("export FIRECRAWL_API_KEY=your_api_key_here")
        return
    
    # Create configuration
    config = Config(
        firecrawl_api_key=api_key,
        output_format="json",
        max_pages=5,
        delay_between_requests=1.5,
        log_level="INFO"
    )
    
    print(f"✅ Configuration created")
    print(f"   - Output format: {config.output_format}")
    print(f"   - Max pages: {config.max_pages}")
    print(f"   - Delay between requests: {config.delay_between_requests}s")
    print(f"   - Output directory: {config.output_directory}")
    print()
    
    try:
        # Initialize crawler
        crawler = PropertyCrawler(config)
        print("✅ PropertyCrawler initialized")
        print()
        
        # Crawl single URL example
        print("🔄 Crawling single URL...")
        single_result = crawler.crawl_url(example_urls[0])
        print(f"✅ Single URL crawled successfully")
        print(f"   - URL: {single_result.get('url', 'N/A')}")
        print(f"   - Status: {single_result.get('success', 'N/A')}")
        print()
        
        # Crawl multiple URLs example
        print("🔄 Crawling multiple URLs...")
        results = crawler.crawl_multiple_urls(example_urls)
        print(f"✅ Crawled {len(results)} URLs successfully")
        print()
        
        # Save results
        print("💾 Saving results...")
        crawler.save_results(results, "example_property_data")
        print("✅ Results saved successfully")
        print()
        
        # Display summary
        print("📊 Crawling Summary:")
        print(f"   - Total URLs processed: {len(results)}")
        print(f"   - Output format: {config.output_format}")
        print(f"   - Output directory: {config.output_directory}")
        print()
        
        print("🎉 Example completed successfully!")
        print("Check the 'data' directory for your crawled results.")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your Firecrawl API key is valid")
        print("2. Ensure the URLs are accessible")
        print("3. Check your internet connection")
        print("4. Review the log files for detailed error information")


if __name__ == "__main__":
    main() 