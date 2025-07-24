from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import scraping
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # show logs in console
    ]
)


app = FastAPI(title="Property FireCrawl Middleware")

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add client-side URL later
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(scraping.router, prefix="/api/scrape", tags=["scraping"])

@app.get("/")
async def root():
    return {"message": "Property FireCrawl API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "property-scraping"}