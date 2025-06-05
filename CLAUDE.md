# Life OS - Sistema de Organização Pessoal

## Overview
Life OS é um sistema modular de linha de comando para organização pessoal, com módulos para diferentes aspectos da vida. Atualmente conta com um módulo de agregação de notícias de tecnologia totalmente funcional, com persistência MongoDB e visualização completa de artigos.

## Quick Start

### ⚡ Installation
```bash
# 1. Clone the repository
git clone <repository-url>
cd life-os

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start MongoDB (optional but recommended)
./scripts/start-mongodb.sh

# 4. Run Life OS
python main.py
```

### 🎯 First Use
1. **Launch Life OS**: Run `python main.py`
2. **Enter News Module**: Select option `1` (📰 Notícias)
3. **View Latest News**: Select option `1` (📰 Últimas notícias)
4. **Read an Article**: Type any article number to view full content
5. **Explore Features**: Try options 2-6 for management and statistics

## Project Structure
```
life-os/
├── main.py                    # Menu principal do Life OS
├── modules/                   # Módulos funcionais do sistema
│   ├── __init__.py
│   └── news.py               # Módulo de notícias com interface completa
├── scrapers/                 # Web scrapers para diferentes sites
│   ├── __init__.py
│   └── tabnews_scraper.py    # Scraper TabNews com extração de artigos detalhados
├── utils/                    # Utilitários centrais
│   ├── __init__.py
│   ├── config.py             # Sistema de configuração centralizado
│   ├── config_manager.py     # Gerencia sites ativos/inativos
│   ├── database_manager.py   # Gerenciador MongoDB com fallbacks
│   └── news_aggregator.py    # Agrega notícias com controle de rate limiting
├── docker/                   # Configuração Docker
│   └── mongo-init.js         # Script de inicialização do MongoDB
├── scripts/                  # Scripts de automação
│   ├── start-mongodb.sh      # Iniciar ambiente MongoDB
│   └── stop-mongodb.sh       # Parar ambiente MongoDB
├── data/                     # Armazenamento local e cache
│   ├── config.json          # Preferências do usuário
│   └── news_cache.json      # Cache de fallback (JSON)
├── .env.example              # Template de configurações
├── docker-compose.yml        # Definição dos containers
└── requirements.txt          # Dependências Python
```

## Módulos do Life OS

### 📰 Notícias (Implementado)
- **Agregador Completo**: Suporte ao TabNews com arquitetura modular
- **Visualização Detalhada**: Leitura completa de artigos e comentários no terminal
- **Persistência Inteligente**: MongoDB com fallback JSON automático
- **Rate Limiting**: Controle de 6 horas para evitar bloqueios
- **Interface Rica**: Navegação por páginas, seleção de artigos, estatísticas
- **Monitoramento**: Dashboard de status do banco e fontes de notícias

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

### Article Data Structures
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

@dataclass
class ArtigoDetalhado:
    titulo: str                    # Full article title
    link: str                     # Article URL
    autor: str                    # Author name
    tempo_postagem: str           # Publishing time
    conteudo_markdown: str        # Full article content in markdown
    comentarios: List[Comentario] # All article comments
    origem: str                   # Source site

@dataclass
class Comentario:
    autor: str                    # Comment author
    conteudo: str                 # Comment content
    tempo_postagem: str           # Comment time
    respostas: List[Comentario]   # Nested replies (future)
```

### System Architecture
- **Three-Tier Persistence**: MongoDB → JSON → Memory cache
- **Rate Limiting**: Configurable update intervals (default: 6 hours)
- **Modular Design**: Easy addition of new scrapers and modules
- **Docker Integration**: Zero-config setup with automated database
- **Environment Management**: Flexible configuration via .env files

## Comandos para Execução

### 🚀 Início Rápido
```bash
# 1. Iniciar MongoDB (recomendado)
./scripts/start-mongodb.sh

# 2. Executar o Life OS
python main.py

# 3. Parar MongoDB quando terminar
./scripts/stop-mongodb.sh
```

### 🧪 Testes e Desenvolvimento
```bash
# Testar apenas o módulo de notícias
python modules/news.py

# Testar scraper básico
python -c "from scrapers.tabnews_scraper import TabNewsScraper; print(TabNewsScraper().scrape_artigos())"

# Testar scraper detalhado
python -c "
from scrapers.tabnews_scraper import TabNewsScraper
scraper = TabNewsScraper()
articles = scraper.scrape_artigos()[:1]
if articles:
    detailed = scraper.scrape_artigo_detalhado(articles[0].link)
    print(f'Título: {detailed.titulo}')
    print(f'Conteúdo: {len(detailed.conteudo_markdown)} chars')
    print(f'Comentários: {len(detailed.comentarios)}')
"

# Testar sistema de configuração
python -c "from utils.config import Config; Config.print_config()"
```

## Future Features

### 📰 News Module Enhancements
- **Additional Scrapers**: Dev.to, Hacker News, Reddit, GitHub Trending
- **AI Classification**: OpenAI-powered tag classification and categorization
- **Advanced Filtering**: Filter by tags, authors, date ranges, content type
- **Search Engine**: Full-text search across cached articles and comments
- **Export Options**: CSV, JSON, PDF, Markdown exports
- **Read Status**: Track read/unread articles and reading progress
- **Favorites System**: Bookmark important articles and comments
- **Trending Analysis**: Identify trending topics and popular discussions

### 🔧 Technical Improvements
- **API Integration**: REST API for external integrations
- **Mobile App**: React Native companion app
- **Browser Extension**: Quick save articles from web browsing
- **RSS Support**: Custom RSS feeds generation
- **Webhook Notifications**: Real-time notifications for new content
- **Analytics Dashboard**: Usage statistics and reading patterns

## Adding New Scrapers

### 1. Basic Scraper Implementation
```python
# scrapers/new_site_scraper.py
from typing import List
from .tabnews_scraper import Artigo

class NewSiteScraper:
    def __init__(self):
        self.base_url = "https://newsite.com"
        self.headers = {'User-Agent': 'LifeOS/1.0'}
    
    def scrape_artigos(self) -> List[Artigo]:
        # Implement scraping logic
        pass
    
    def scrape_artigo_detalhado(self, url: str) -> Optional[ArtigoDetalhado]:
        # Implement detailed scraping
        pass
```

### 2. Register in System
```python
# utils/news_aggregator.py
self.scrapers = {
    "TabNews": TabNewsScraper(),
    "NewSite": NewSiteScraper(),  # Add new scraper
}

# utils/config_manager.py
self.available_sites = ["TabNews", "NewSite"]  # Add to available sites
```

### 3. Update Configuration
```bash
# Add to .env if needed
NEWSITE_API_KEY=your_api_key_here
NEWSITE_MAX_ARTICLES=50
```

## Dependencies

### Core Dependencies
```bash
pip install -r requirements.txt
```

- **requests** (2.31.0): HTTP requests and web scraping
- **beautifulsoup4** (4.12.2): HTML parsing and content extraction
- **rich** (13.7.0): Terminal UI components and formatting
- **pymongo** (4.6.1): MongoDB database integration
- **python-dotenv** (1.0.0): Environment variables management

### Development Dependencies
- **Docker**: Container management for MongoDB
- **docker-compose**: Multi-container orchestration

## Current Features

### 📰 News Module - Complete Functionality

**📋 Article Management**
- **Smart Aggregation**: Automatically collect articles from configured sources
- **Rate Limiting**: 6-hour intervals to prevent site blocking
- **Duplicate Prevention**: Smart filtering to avoid duplicate articles
- **Pagination**: Navigate through large article collections efficiently

**📖 Enhanced Reading Experience**
- **Full Article View**: Read complete articles within the terminal
- **Markdown Formatting**: Proper text formatting with headers, lists, quotes
- **Comment System**: View all article comments with author information
- **Interactive Navigation**: Easy switching between content and comments

**💾 Intelligent Persistence**
- **MongoDB Integration**: Production-ready database with indexes
- **Automatic Fallback**: Seamless fallback to JSON when DB unavailable
- **Data Consistency**: Maintain article history and reading state
- **Performance Optimization**: Smart caching and efficient queries

**🔧 Management Tools**
- **Source Management**: Add/remove news sources dynamically
- **Statistics Dashboard**: Monitor update times and article counts
- **Force Updates**: Manual refresh capability for immediate updates
- **Configuration**: Flexible settings via environment variables

**🎛️ User Interface**
- **Rich Terminal UI**: Beautiful, intuitive command-line interface
- **Responsive Design**: Adaptive layout for different terminal sizes
- **Keyboard Navigation**: Efficient keyboard-only operation
- **Status Indicators**: Clear feedback on system state and operations

## MongoDB Configuration

### 🐳 Docker (Recomendado - Mais Fácil)
```bash
# Iniciar MongoDB com Docker
./scripts/start-mongodb.sh

# Parar MongoDB
./scripts/stop-mongodb.sh

# O script automaticamente:
# - Cria containers MongoDB + Mongo Express
# - Configura usuário e banco de dados
# - Cria índices otimizados
# - Interface web em http://localhost:8081
```

### 🔧 Configuração Manual
1. Copiar `.env.example` para `.env`
2. Ajustar variáveis de ambiente conforme necessário
3. O sistema usa automaticamente as configurações do `.env`

### 📂 Estrutura de Configuração
```
├── .env                    # Configurações locais (não versionado)
├── .env.example           # Template de configurações
├── docker-compose.yml     # Definição dos containers
├── docker/
│   └── mongo-init.js      # Script de inicialização do MongoDB
└── scripts/
    ├── start-mongodb.sh   # Iniciar MongoDB
    └── stop-mongodb.sh    # Parar MongoDB
```

### ⚙️  Variáveis de Ambiente
```bash
# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=lifeos
MONGODB_USERNAME=lifeos_app
MONGODB_PASSWORD=lifeos_app_password

# Configurações da aplicação
NEWS_UPDATE_INTERVAL_HOURS=6
MAX_ARTICLES_PER_SOURCE=50
```

### 🔄 Sistema de Fallback
- **Primeira opção**: MongoDB com autenticação
- **Segunda opção**: MongoDB sem autenticação
- **Terceira opção**: Arquivo JSON local
- **Resultado**: Sistema sempre funciona independente da configuração

### 🛡️ Configurações do Sistema de Cache
- **Controle de Tempo**: Configurável via `NEWS_UPDATE_INTERVAL_HOURS` (padrão: 6h)
- **Persistência**: MongoDB para produção, JSON para fallback
- **Prevenção de Rate Limiting**: Evita requests excessivos aos sites de notícias
- **Monitoramento**: Interface para visualizar status e estatísticas

## Troubleshooting

### 🔧 Common Issues

**MongoDB Connection Problems**
```bash
# Check if MongoDB is running
docker ps | grep lifeos-mongodb

# Restart MongoDB
./scripts/stop-mongodb.sh
./scripts/start-mongodb.sh

# Check MongoDB logs
docker-compose logs mongodb
```

**Permission Issues with Scripts**
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

**Python Dependencies Issues**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**No Articles Loading**
```bash
# Force update manually
python -c "
from utils.config_manager import ConfigManager
from utils.news_aggregator import NewsAggregator
config = ConfigManager()
news = NewsAggregator(config)
news.force_update_all()
"

# Check if TabNews is accessible
curl -I https://www.tabnews.com.br
```

### 📊 System Status Check
```bash
# Check configuration
python -c "from utils.config import Config; Config.print_config()"

# Test database connection
python -c "
from utils.database_manager import DatabaseManager
db = DatabaseManager()
print('MongoDB connected:', db.is_connected())
"

# Check available articles
python -c "
from utils.config_manager import ConfigManager
from utils.news_aggregator import NewsAggregator
news = NewsAggregator(ConfigManager())
stats = news.get_database_stats()
print('Sources:', len(stats.get('sources', {})))
"
```

### 🆘 Getting Help
- **Documentation**: Check this CLAUDE.md file
- **Logs**: Check terminal output for error messages
- **Database Interface**: http://localhost:8081 (if MongoDB is running)
- **System Status**: Use option 6 in News Module for diagnostics