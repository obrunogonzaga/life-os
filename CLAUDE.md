# Life OS - Sistema de Organização Pessoal

## Overview
Life OS é um sistema modular de linha de comando para organização pessoal, com módulos para diferentes aspectos da vida. Atualmente conta com um módulo de agregação de notícias de tecnologia totalmente funcional.

## Project Structure
```
life-os/
├── main.py                 # Menu principal do Life OS
├── news_menu.py           # Módulo de notícias (antigo main.py)
├── scrapers/              # Web scrapers para diferentes sites
│   └── tabnews_scraper.py # Implementação do scraper TabNews
├── utils/                 # Utilitários centrais
│   ├── config_manager.py  # Gerencia sites ativos/inativos
│   └── news_aggregator.py # Agrega notícias de múltiplas fontes
├── data/                  # Armazenamento de cache e configuração
│   ├── config.json       # Preferências do usuário
│   └── news_cache.json   # Cache de artigos de notícias
└── requirements.txt       # Dependências Python
```

## Módulos do Life OS

### 📰 Notícias (Implementado)
- Agregador de notícias de tecnologia
- Suporte atual: TabNews
- Cache inteligente de 5 minutos
- Interface interativa para gerenciar fontes

### 📅 Agenda (Em breve)
- Gerenciamento de compromissos e eventos

### ✅ Tarefas (Em breve)
- Sistema de gerenciamento de tarefas e projetos

### 💰 Finanças (Em breve)
- Controle financeiro pessoal

### 📝 Notas (Em breve)
- Sistema de anotações e documentação pessoal

### 🎯 Hábitos (Em breve)
- Rastreamento e desenvolvimento de hábitos

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

## Comandos para Execução
```bash
# Executar o Life OS
python main.py

# Testar apenas o módulo de notícias
python news_menu.py

# Testar scraper diretamente
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