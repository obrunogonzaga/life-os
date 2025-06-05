# Widia News - Project Documentation

## Overview
Widia News is a tech news aggregator that collects articles from multiple sources into a unified interface. Currently supports TabNews with a modular architecture for easy expansion.

## Project Structure
```
widia-news/
├── main.py                 # Interactive CLI menu
├── scrapers/              # Web scrapers for different sites
│   └── tabnews_scraper.py # TabNews scraper implementation
├── utils/                 # Core utilities
│   ├── config_manager.py  # Manages active/inactive sites
│   └── news_aggregator.py # Aggregates news from multiple sources
├── data/                  # Cache and configuration storage
│   ├── config.json       # User preferences
│   └── news_cache.json   # Cached news articles
└── requirements.txt       # Python dependencies
```

## Key Components

### Article Data Structure
```python
@dataclass
class Artigo:
    titulo: str          # Article title
    link: str           # Full URL
    comentarios: int    # Comment count
    autor: str          # Author username
    tempo_postagem: str # Relative time (e.g., "2 horas atrás")
    origem: str         # Source site (e.g., "TabNews")
    tags: Optional[List[str]] = None  # Future: AI classification
```

### Configuration
- **Cache Duration**: 5 minutes (configurable)
- **Max Articles**: 50 per site (configurable)
- **Active Sites**: User-controlled list of sources

## Testing Commands
```bash
# Run the application
python main.py

# Test scraper directly
python -c "from scrapers.tabnews_scraper import TabNewsScraper; print(TabNewsScraper().scrape_artigos())"
```

## Future Features
- Additional scrapers (Dev.to, Hacker News, etc.)
- AI-powered tag classification using OpenAI
- Article filtering by tags
- Search functionality
- Export options (CSV, JSON)
- Read status tracking

## Adding New Scrapers
1. Create new file in `scrapers/` directory
2. Implement scraper class with `scrape_artigos()` method returning `List[Artigo]`
3. Add to `NewsAggregator.scrapers` dictionary
4. Add to `ConfigManager.available_sites`

## Dependencies
- requests: HTTP requests
- beautifulsoup4: HTML parsing
- rich: Terminal UI components