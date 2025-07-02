import os
from typing import List, Dict, Any

class Config:
    """Configuration settings for the scraper application."""
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://scraper:scraper_password@localhost:5432/scraper_db"
    )
    
    # Firecrawl Configuration
    FIRECRAWL_URL = os.getenv("FIRECRAWL_URL", "http://localhost:3002")
    
    # Redis Configuration (for job queuing)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Scraping Configuration
    SCRAPING_TARGETS: List[Dict[str, Any]] = [
        {
            "name": "TechCrunch AI News",
            "base_url": "https://techcrunch.com/category/artificial-intelligence/",
            "type": "crawl",
            "limit": 20,
            "schedule": "hourly",
            "formats": ["markdown"],
            "extract_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "publish_date": {"type": "string"},
                    "summary": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        {
            "name": "ArXiv AI Papers",
            "base_url": "https://arxiv.org/list/cs.AI/recent",
            "type": "crawl",
            "limit": 10,
            "schedule": "daily",
            "formats": ["markdown"],
            "pdf_extraction": True
        }
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/scraper.log"
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "30"))
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
    
    # Optional API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

    @classmethod
    def get_target_by_name(cls, name: str) -> Dict[str, Any]:
        """Get scraping target configuration by name."""
        for target in cls.SCRAPING_TARGETS:
            if target["name"] == name:
                return target
        raise ValueError(f"Scraping target '{name}' not found")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings."""
        required_vars = [
            "DATABASE_URL",
            "FIRECRAWL_URL"
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
        
        return True