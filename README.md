# 🧠 Life OS - Sistema de Organização Pessoal

> Sistema modular de linha de comando para organização pessoal com agregação inteligente de notícias

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![Rich](https://img.shields.io/badge/Terminal-Rich%20UI-orange.svg)](https://rich.readthedocs.io)

## 🚀 Quick Start

```bash
# 1. Clone e instale dependências
git clone <repository-url>
cd life-os
pip install -r requirements.txt

# 2. Inicie o MongoDB (recomendado)
./scripts/start-mongodb.sh

# 3. Execute o Life OS
python main.py
```

## ✨ Features

### 📰 **Módulo de Notícias** (Implementado)
- 🔄 **Agregação Inteligente**: Coleta automática do TabNews com rate limiting e TTL de 5 dias
- 📖 **Leitura Completa**: Visualização instantânea de artigos e comentários no terminal
- 💾 **Persistência Dual**: MongoDB local/remoto com cache detalhado e fallback JSON
- 🌐 **MongoDB Remoto**: Suporte completo ao Coolify/Hostinger para acesso universal
- 🎛️ **Interface Rica**: Navegação interativa com atalho 'M' para menu principal
- ⚡ **Performance**: Cache inteligente com atualizações de 6h e limpeza automática
- 🎯 **Extração Avançada**: 89% de taxa de extração de comentários sem duplicatas
- 🧪 **Ferramentas Diagnóstico**: Utilitário completo para testar conexões MongoDB

### 🔮 **Módulos Futuros**
- 📅 **Agenda**: Gerenciamento de compromissos e eventos
- ✅ **Tarefas**: Sistema de gerenciamento de tarefas e projetos
- 💰 **Finanças**: Controle financeiro pessoal
- 📝 **Notas**: Sistema de anotações e documentação
- 🎯 **Hábitos**: Rastreamento e desenvolvimento de hábitos

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "🖥️ User Interface"
        UI[Rich Terminal Interface]
        MAIN[Main Menu - Life OS]
    end
    
    subgraph "📰 News Module"
        NEWS[News Menu]
        PAGINATE[Paginated Article List]
        DETAIL[Article Detail View]
        COMMENTS[Comments View]
        STATS[Statistics Dashboard]
    end
    
    subgraph "🔄 Data Processing"
        AGG[News Aggregator]
        SCRAPER[TabNews Scraper]
        RATE[Rate Limiter<br/>6h intervals]
    end
    
    subgraph "💾 Data Layer"
        MONGO[(MongoDB<br/>Primary)]
        JSON[(JSON Cache<br/>Fallback)]
        CONFIG[Config Manager]
    end
    
    subgraph "🐳 Infrastructure"
        DOCKER[Docker Compose]
        MONGOEX[Mongo Express<br/>:8081]
        ENV[Environment<br/>Variables]
    end
    
    subgraph "🌐 External"
        TABNEWS[TabNews.com.br]
    end
    
    %% User Flow
    UI --> MAIN
    MAIN --> NEWS
    NEWS --> PAGINATE
    PAGINATE --> DETAIL
    DETAIL --> COMMENTS
    NEWS --> STATS
    
    %% Data Flow
    AGG --> SCRAPER
    SCRAPER --> TABNEWS
    SCRAPER --> RATE
    AGG --> MONGO
    AGG --> JSON
    NEWS --> AGG
    
    %% Configuration
    CONFIG --> ENV
    CONFIG --> AGG
    
    %% Infrastructure
    DOCKER --> MONGO
    DOCKER --> MONGOEX
    ENV --> CONFIG
    
    %% Fallback Flow
    MONGO -.->|"Fallback"| JSON
    
    %% Styling
    classDef interface fill:#e1f5fe
    classDef module fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef infra fill:#fff3e0
    classDef external fill:#ffebee
    
    class UI,MAIN interface
    class NEWS,PAGINATE,DETAIL,COMMENTS,STATS module
    class AGG,SCRAPER,RATE,MONGO,JSON,CONFIG data
    class DOCKER,MONGOEX,ENV infra
    class TABNEWS external
```

## 🔧 Architecture Components

### **User Interface Layer**
- **Rich Terminal UI**: Interface moderna com cores e formatação
- **Modular Navigation**: Menu principal → Módulos → Funcionalidades
- **Responsive Design**: Adaptável a diferentes tamanhos de terminal

### **News Module Workflow**
```mermaid
sequenceDiagram
    participant User
    participant NewsModule
    participant Aggregator
    participant Scraper
    participant Database
    participant TabNews
    
    User->>NewsModule: View Latest News
    NewsModule->>Aggregator: Get Articles
    
    alt Less than 6 hours since last update
        Aggregator->>Database: Retrieve Cached Articles
        Database-->>Aggregator: Return Articles
    else Need to Update
        Aggregator->>Scraper: Scrape New Articles
        Scraper->>TabNews: HTTP Request
        TabNews-->>Scraper: HTML Response
        Scraper-->>Aggregator: Parsed Articles
        Aggregator->>Database: Store Articles
    end
    
    Aggregator-->>NewsModule: Return Articles
    NewsModule-->>User: Display Paginated List
    
    User->>NewsModule: Select Article (Number)
    NewsModule->>Scraper: Get Article Details
    Scraper->>TabNews: Fetch Full Article
    TabNews-->>Scraper: Article HTML
    Scraper-->>NewsModule: Article + Comments
    NewsModule-->>User: Display Full Article
```

### **Data Flow & Persistence**
```mermaid
flowchart LR
    subgraph "🔄 Data Sources"
        TN[TabNews API]
    end
    
    subgraph "⚙️ Processing"
        SC[Scraper]
        AG[Aggregator]
        RL[Rate Limiter]
    end
    
    subgraph "💾 Storage"
        MG[(MongoDB)]
        JS[JSON Cache]
        CF[Config Files]
    end
    
    subgraph "🎛️ Management"
        ST[Statistics]
        UP[Updates]
        FB[Fallback]
    end
    
    TN --> SC
    SC --> AG
    AG --> RL
    RL --> MG
    MG -.->|Failure| JS
    AG --> CF
    
    MG --> ST
    JS --> FB
    ST --> UP
    
    classDef source fill:#ffebee
    classDef process fill:#e3f2fd
    classDef storage fill:#e8f5e8
    classDef mgmt fill:#f3e5f5
    
    class TN source
    class SC,AG,RL process
    class MG,JS,CF storage
    class ST,UP,FB mgmt
```

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.8+**
- **Docker & Docker Compose** (para modo local)
- **Git**
- **Servidor Coolify/Hostinger** (para modo remoto - opcional)

### Step-by-Step Installation

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd life-os
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose Database Mode**

   #### 🏠 **Local Mode** (Recomendado para começar)
   ```bash
   cp .env.example .env
   # DATABASE_MODE=local (padrão)
   
   # Start MongoDB
   ./scripts/start-mongodb.sh
   ```

   #### 🌐 **Remote Mode** (Para acesso universal)
   ```bash
   cp .env.remote_example .env
   # Configure suas credenciais do Coolify/Hostinger
   
   # Test connection
   python utils/test_connection.py "sua-connection-string"
   ```

4. **Launch Life OS**
   ```bash
   python main.py
   ```

### Alternative: JSON-Only Mode
```bash
# Skip MongoDB setup and run with JSON fallback
python main.py
```

### 📚 Setup Guides
- **Remote MongoDB**: [Guia completo Coolify/Hostinger](docs/REMOTE_MONGODB_SETUP.md)
- **Local Development**: Use configuração padrão com Docker

## 📖 Usage Guide

### Basic Navigation
1. **Main Menu**: Choose module (currently only News available)
2. **News Module**: 
   - `1` - View latest articles (with instant cache loading)
   - `2-5` - Manage sources and settings
   - `6` - View database statistics (local/remote) with cache metrics
   - `M` - Return to main menu from any submenu
3. **Article List**: Type article number to read full content instantly
4. **Article View**: Switch between content and comments with enhanced navigation

### Database Configuration
```bash
# Ver configuração atual
python -c "from utils.config import Config; Config.print_config()"

# Testar conexão MongoDB
python utils/test_connection.py "mongodb://connection-string"

# Alternar entre local/remoto
# Edite DATABASE_MODE no .env
```

### Advanced Features
- **Force Update**: Option 5 in News Menu
- **Statistics**: Option 6 shows MongoDB status and update times
- **Source Management**: Add/remove news sources dynamically

## 🔧 Configuration

### Database Mode Selection

O Life OS suporta dois modos de banco de dados:

#### 🏠 **Local Mode** (Padrão)
```bash
# .env
DATABASE_MODE=local
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=lifeos
MONGODB_USERNAME=lifeos_app
MONGODB_PASSWORD=lifeos_app_password
```

#### 🌐 **Remote Mode** (Coolify/Hostinger)
```bash
# .env
DATABASE_MODE=remote
REMOTE_MONGODB_HOST=seu-servidor.hostinger.com
REMOTE_MONGODB_PORT=27017
REMOTE_MONGODB_DATABASE=lifeos
REMOTE_MONGODB_USERNAME=lifeos_user
REMOTE_MONGODB_PASSWORD=sua-senha-segura

# Ou usar URI completa:
REMOTE_MONGODB_URI=mongodb://user:pass@host:port/database
```

### Application Settings
```bash
NEWS_UPDATE_INTERVAL_HOURS=6
MAX_ARTICLES_PER_SOURCE=50
DEBUG=false
```

### Infrastructure Options

#### 🐳 **Local (Docker)**
- **MongoDB**: Local database (port 27017)
- **Mongo Express**: Web interface (http://localhost:8081)
- **Uso**: Desenvolvimento e testes

#### ☁️ **Remote (Coolify/Hostinger)**
- **MongoDB**: Servidor dedicado remoto
- **Acesso**: Via internet de qualquer lugar
- **Uso**: Produção e acesso universal
- **Setup**: Ver [Guia de Configuração](docs/REMOTE_MONGODB_SETUP.md)

## 📊 Monitoring

### Built-in Statistics
- **MongoDB connection status** (local/remote)
- **Database mode**: LOCAL ou REMOTE
- **Last update times** per source
- **Article count** per source com cache metrics
- **Update intervals** and next scheduled updates

### External Monitoring

#### 🏠 Local Mode
- **Mongo Express**: http://localhost:8081 (database web interface)
- **Docker Logs**: `docker-compose logs mongodb`

#### 🌐 Remote Mode
- **Coolify Dashboard**: Interface web do servidor
- **Connection Testing**: `python utils/test_connection.py`
- **System Status**: News Module → Option 6

## 🚨 Troubleshooting

### Common Issues

**MongoDB Connection Failed**

*Local Mode:*
```bash
# Check Docker status
docker ps | grep lifeos-mongodb

# Restart MongoDB
./scripts/stop-mongodb.sh
./scripts/start-mongodb.sh
```

*Remote Mode:*
```bash
# Test connection
python utils/test_connection.py "sua-connection-string"

# Check configuration
python -c "from utils.config import Config; Config.print_config()"

# Verify Coolify service status
# Via Coolify dashboard
```

**No Articles Loading**
```bash
# Force manual update
python -c "
from utils.news_aggregator import NewsAggregator
from utils.config_manager import ConfigManager
news = NewsAggregator(ConfigManager())
news.force_update_all()
"
```

**Permission Denied on Scripts**
```bash
chmod +x scripts/*.sh
```

## 🌐 MongoDB Remote Integration

### ✨ **Acesso Universal aos Dados**
Com o suporte ao MongoDB remoto via Coolify/Hostinger, o Life OS agora oferece:

- **📱 Multi-dispositivo**: Acesse seus dados de qualquer lugar
- **☁️ Backup automático**: Dados seguros no servidor remoto 24/7
- **🚀 Performance**: MongoDB v7.0.21 em servidor dedicado
- **🔄 Sincronização**: Automática entre múltiplos clientes
- **🔧 Flexibilidade**: Alterna facilmente entre local e remoto

### 🛠️ **Configuração Rápida**
```bash
# 1. Configurar modo remoto
cp .env.remote_example .env
# Editar credenciais do Coolify

# 2. Testar conexão
python utils/test_connection.py "sua-connection-string"

# 3. Executar Life OS
python main.py
```

### 📚 **Documentação Completa**
- [📖 Guia Setup Remoto](docs/REMOTE_MONGODB_SETUP.md) - Como configurar MongoDB no Coolify/Hostinger
- [🧪 Test Connection](utils/test_connection.py) - Ferramenta de diagnóstico de conexão
- [⚙️ Config Management](utils/config.py) - Sistema de configuração dual

## 🔮 Roadmap

### Phase 1: News Enhancement ✅
- [x] MongoDB integration with Docker and TTL indexes
- [x] **Remote MongoDB support** with Coolify/Hostinger integration
- [x] **Dual database mode** (local/remote) with automatic fallback
- [x] Full article reading with comments and 89% extraction rate
- [x] Rate limiting, caching, and automatic cleanup
- [x] Statistics and monitoring with cache metrics
- [x] Rich terminal interface with direct navigation shortcuts
- [x] Article details caching system with 6-hour updates
- [x] Enhanced comment extraction with duplicate filtering
- [x] **MongoDB connection testing utility** for diagnostics

### Phase 2: Multi-Source News 🚧
- [ ] Dev.to scraper
- [ ] Hacker News integration
- [ ] Reddit technology subreddits
- [ ] GitHub Trending

### Phase 3: Additional Modules 📋
- [ ] Calendar/Agenda module
- [ ] Task management system
- [ ] Personal finance tracker
- [ ] Note-taking system
- [ ] Habit tracker

### Phase 4: Advanced Features 🎯
- [ ] AI-powered content classification
- [ ] REST API for external integrations
- [ ] Mobile companion app
- [ ] Browser extension

## 🤝 Contributing

### Adding New Scrapers
1. Create scraper class in `scrapers/`
2. Implement `scrape_artigos()` and `scrape_artigo_detalhado()` methods
3. Register in `NewsAggregator.scrapers`
4. Add to `ConfigManager.available_sites`

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -c "from scrapers.tabnews_scraper import TabNewsScraper; print('✅ Scraper OK')"

# Check system configuration
python -c "from utils.config import Config; Config.print_config()"

# Test MongoDB connection (local or remote)
python utils/test_connection.py "mongodb://connection-string"

# Switch database modes for testing
# Edit DATABASE_MODE in .env file
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **TabNews**: Primary news source (https://tabnews.com.br)
- **Rich**: Beautiful terminal interfaces (https://rich.readthedocs.io)
- **MongoDB**: Robust document database (local & remote)
- **Docker**: Containerization platform for local development
- **Coolify**: Self-hosted PaaS for remote MongoDB deployment
- **Hostinger**: Cloud hosting infrastructure

---

<div align="center">

**[⬆ Back to Top](#-life-os---sistema-de-organização-pessoal)**

Made with ❤️ using Python, MongoDB (Local & Remote), and Rich Terminal UI

</div>