from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from config import Config

# Database setup
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)

class ScrapedContent(Base):
    """Database model for scraped content."""
    __tablename__ = "scraped_content"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    page_metadata = Column(JSON, nullable=True)  # ← FIXED: renamed from 'metadata'
    extracted_data = Column(JSON, nullable=True)
    source_name = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    word_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

class ScrapeJob(Base):
    """Database model for scraping jobs."""
    __tablename__ = "scrape_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    job_type = Column(String, nullable=False)
    status = Column(String, default='pending')
    firecrawl_job_id = Column(String, nullable=True)
    pages_scraped = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def save_scraped_content(self, content_data: dict) -> int:
        """Save scraped content to database."""
        session = self.get_session()
        try:
            # Check if URL already exists
            existing = session.query(ScrapedContent).filter(
                ScrapedContent.url == content_data["url"]
            ).first()
            
            if existing:
                # Update existing record
                for key, value in content_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                content_id = existing.id
                logger.info(f"Updated existing content for URL: {content_data['url']}")
            else:
                # Create new record
                content = ScrapedContent(**content_data)
                session.add(content)
                session.flush()
                content_id = content.id
                logger.info(f"Saved new content for URL: {content_data['url']}")
            
            session.commit()
            return content_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving scraped content: {e}")
            raise
        finally:
            session.close()
    
    def get_content_stats(self) -> dict:
        """Get content statistics."""
        session = self.get_session()
        try:
            total_content = session.query(ScrapedContent).count()
            total_jobs = session.query(ScrapeJob).count()
            completed_jobs = session.query(ScrapeJob).filter(
                ScrapeJob.status == 'completed'
            ).count()
            
            return {
                "total_content": total_content,
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0
            }
        finally:
            session.close()