#!/usr/bin/env python3
"""
Web Scraper Application using local Firecrawl and PostgreSQL
"""

import logging
import time
import schedule
from datetime import datetime
from typing import Dict, List, Any, Optional
from firecrawl import FirecrawlApp
from database import DatabaseManager, ScrapedContent, ScrapeJob
from config import Config
import click
import sys

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    """Main web scraper application."""
    
    def __init__(self):
        # For local Firecrawl, use a dummy API key
        self.firecrawl = FirecrawlApp(
            api_key="dummy-key-for-local-use", 
            api_url=Config.FIRECRAWL_URL
        )
        self.db = DatabaseManager()
        self.db.create_tables()
        logger.info("WebScraper initialised")
    
    def scrape_url(self, url: str, formats: List[str] = None, extract_schema: Dict = None) -> Optional[Dict]:
        """Scrape a single URL."""
        formats = formats or ["markdown"]
        
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Use the updated API for firecrawl-py 2.x
            if extract_schema:
                # For structured extraction, add json format
                if "json" not in formats:
                    formats.append("json")
                
                from firecrawl import JsonConfig
                json_config = JsonConfig(schema=extract_schema)
                
                result = self.firecrawl.scrape_url(
                    url, 
                    formats=formats,
                    json_options=json_config
                )
            else:
                result = self.firecrawl.scrape_url(url, formats=formats)
            
            if result and hasattr(result, 'data'):
                data = result.data
                
                # Prepare data for database
                content_data = {
                    "url": url,
                    "title": data.get("metadata", {}).get("title") if data.get("metadata") else None,
                    "content": data.get("markdown"),
                    "html_content": data.get("html"),
                    "page_metadata": data.get("metadata", {}),
                    "extracted_data": data.get("json"),
                    "content_type": self._detect_content_type(url, data),
                    "word_count": len(data.get("markdown", "").split()) if data.get("markdown") else 0
                }
                
                # Save to database
                content_id = self.db.save_scraped_content(content_data)
                logger.info(f"Successfully scraped and saved URL: {url} (ID: {content_id})")
                
                return content_data
            else:
                logger.warning(f"No content returned for URL: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return None
    
    def _detect_content_type(self, url: str, data: dict) -> str:
        """Detect the type of content based on URL and result."""
        url_lower = url.lower()
        
        if url_lower.endswith('.pdf'):
            return 'pdf'
        elif 'news' in url_lower or 'blog' in url_lower or 'article' in url_lower:
            return 'article'
        elif 'docs' in url_lower or 'documentation' in url_lower:
            return 'documentation'
        elif 'arxiv.org' in url_lower:
            return 'research_paper'
        else:
            return 'webpage'
    
    def get_stats(self) -> Dict:
        """Get scraping statistics."""
        return self.db.get_content_stats()
    
    def run_daemon(self):
        """Run as a background daemon service."""
        logger.info("Starting scraper daemon...")
        logger.info("Scraper is ready and waiting for commands.")
        logger.info("Use 'docker-compose exec scraper python scraper.py scrape <URL>' to scrape")
        
        # Keep the service running
        try:
            while True:
                time.sleep(60)  # Check every minute
                # You could add scheduled scraping here if needed
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")

# CLI Interface
@click.group()
def cli():
    """Web Scraper CLI."""
    pass

@cli.command()
@click.argument('url')
@click.option('--formats', multiple=True, default=['markdown'], help='Output formats')
def scrape(url, formats):
    """Scrape a single URL."""
    scraper = WebScraper()
    result = scraper.scrape_url(url, list(formats))
    
    if result:
        click.echo(f"✅ Successfully scraped: {url}")
        click.echo(f"Title: {result.get('title', 'N/A')}")
        click.echo(f"Word count: {result.get('word_count', 0)}")
        click.echo(f"Content preview: {result.get('content', '')[:200]}...")
    else:
        click.echo(f"❌ Failed to scrape: {url}")

@cli.command()
def stats():
    """Show scraping statistics."""
    scraper = WebScraper()
    stats = scraper.get_stats()
    
    click.echo("📊 Scraping Statistics:")
    click.echo(f"   Total content items: {stats['total_content']}")
    click.echo(f"   Total jobs: {stats['total_jobs']}")
    click.echo(f"   Completed jobs: {stats['completed_jobs']}")
    click.echo(f"   Success rate: {stats['success_rate']:.2%}")

@cli.command()
def daemon():
    """Run as background daemon service."""
    scraper = WebScraper()
    scraper.run_daemon()

if __name__ == "__main__":
    # Validate configuration
    try:
        Config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    
    # If no arguments provided, run as daemon
    if len(sys.argv) == 1:
        scraper = WebScraper()
        scraper.run_daemon()
    else:
        # Run CLI
        cli()