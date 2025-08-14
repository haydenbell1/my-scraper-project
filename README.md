# My Web Scraper Project

A basic web scraping application using local Firecrawl and PostgreSQL database. 

TODO: Will integrate social media api once i've played around with it and know how it works

## Features

- 🕷️ Web scraping using local Firecrawl instance
- 🗄️ PostgreSQL database for data storage
- 🐳 Docker containerisation for easy deployment
- 📊 Clean data extraction and storage
- 🔄 Automated scraping workflows

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/my-scraper-project.git
   cd my-scraper-project
   ```

2. Initialise and update Firecrawl submodule:
   ```bash
   git submodule update --init --recursive
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Run a test scrape:
   ```bash
   docker-compose exec scraper python scraper.py scrape https://example.com
   ```

## Services

- **Firecrawl API**: http://localhost:3002
- **Scraper App**: Runs scheduled jobs
- **PostgreSQL**: Database on port 5432
- **Queue Admin**: http://localhost:3002/admin/your-key/queues

## Project Structure

```
my-scraper-project/
├── scraper/           # Main application code
├── firecrawl/         # Firecrawl submodule
├── data/              # Database persistence
└── docker-compose.yml # Service definitions
```

## Configuration

Edit `scraper/config.py` to customise:
- Database connection
- Scraping targets
- Schedule settings
- API keys (optional)

## Usage Examples

```python
from scraper import WebScraper

scraper = WebScraper()

# Scrape a single page
result = scraper.scrape_url("https://example.com")

# Crawl an entire site
results = scraper.crawl_site("https://docs.example.com", limit=50)

# Extract structured data
data = scraper.extract_structured_data("https://product-page.com")
```

## Development

```bash
# View logs
docker-compose logs -f scraper

# Access database
docker-compose exec db psql -U scraper -d scraper_db

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up --build
```

## License

MIT License - see LICENSE file for details.
