# Property Firecrawl

A Python package for property data web crawling using the Firecrawl API in stealth mode.

## Features

- 🔥 **Firecrawl Integration**: Leverages the powerful Firecrawl  API with automatic stealth mode fallback
- 🏠 **Property-Focused**:  Specifically designed for reliable Zillow property scraping
- ⚡ **Rate Limiting**: Built-in delays and retry mechanisms to respect website limits

## Project Structure

```
property-firecrawl/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── __init__.py
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
├── routers/
│   └── scraping.py       # API endpoints
└── services/
    └── firecrawl.py        # FireCrawl integration
```

## Installation

### 1. Clone and Setup

1. Clone this repository:
```bash
git clone https://github.com/djblanc360/property-firecrawl.git
cd property-firecrawl
```

2. Install the package:
```bash
pip install -e .
```
for Max
```bash
pip3 install -e .
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn gunicorn httpx python-dotenv firecrawl-py
```

### 3. Environment Configuration

Create a `.env` file:

```bash
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

Get your API key from [FireCrawl](https://firecrawl.dev/).

## Usage

### Starting the Server

**Development:**
```bash
uvicorn main:app --reload --port 8000
```

**Production (with Gunicorn):**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### API Endpoints

#### Scrape Single Zillow Property
```http
POST /api/scrape/zillow
Content-Type: application/json

{
  "zillow_url": "https://www.zillow.com/homedetails/123-main-st-city-state-12345/123456789_zpid/"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://www.zillow.com/homedetails/...",
  "property_data": {
    "address": "123 Main St, City, State",
    "price": "$500,000",
    "bedrooms": 3,
    "bathrooms": 2.5,
    "square_feet": 1800,
    "description": "Beautiful family home...",
    "images": ["https://..."]
  },
  "timestamp": "2025-07-20T..."
}
```

#### Batch Scrape Multiple Properties
```http
POST /api/scrape/zillow/batch
Content-Type: application/json

[
  "https://www.zillow.com/homedetails/property1/",
  "https://www.zillow.com/homedetails/property2/"
]
```

### Local Development
```bash
# Install dependencies
pip install fastapi uvicorn gunicorn httpx python-dotenv firecrawl-py

# Run with auto-reload
uvicorn main:app --reload

# Test the API
curl -X POST "http://localhost:8000/api/scrape/zillow" \
  -H "Content-Type: application/json" \
  -d '{"zillow_url": "https://www.zillow.com/homedetails/..."}'
```

### Testing with Different URLs
The middleware validates that URLs are Zillow property pages (`zillow.com/homedetails/`) and will return a 400 error for invalid URLs.

### Client-Side Integration (TypeScript)

For TanStack Start or any TypeScript client:

```typescript
// Server function to scrape single property
export async function scrapeZillowProperty(
  address: string,
  city: string,
  state: string,
  zip: string
) {
  const response = await fetch('https://your-middleware.render.com/api/scrape/zillow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      address,
      city,
      state,
      zip
    })
  });
  
  if (!response.ok) {
    throw new Error(`Scraping failed: ${response.statusText}`);
  }
  
  return response.json();
}

// Server function to scrape multiple properties
export async function scrapeMultipleProperties(urls: string[]) {
  const response = await fetch('https://your-middleware.render.com/api/scrape/zillow/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(urls)
  });
  
  return response.json();
}
```


# Todos

* setup gunicorn before deploying to Render
* batch scrap multiple properties?
* add client-side urls
* rate limiting
* error handling