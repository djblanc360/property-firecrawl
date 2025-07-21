from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import scraping
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Property FireCrawl Middleware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add client-side URL later
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(scraping.router, prefix="/api/scrape", tags=["scraping"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "property-scraping"}