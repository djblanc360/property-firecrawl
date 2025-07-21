from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    firecrawl_api_key: str
    allowed_origins: list[str] = ["http://localhost:3000"]
    
    # FireCrawl specific settings
    use_stealth_mode: bool = True
    use_premium_proxies: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()