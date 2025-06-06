# Life OS - Sistema de Organização Pessoal

## Overview
Life OS é um sistema modular de linha de comando para organização pessoal, com módulos para diferentes aspectos da vida. Atualmente possui módulos totalmente funcionais de notícias de tecnologia e gerenciamento de tarefas integrado ao Todoist, além de ferramentas avançadas de gerenciamento MongoDB.

## Quick Start

### ⚡ Installation
```bash
# 1. Clone the repository
git clone <repository-url>
cd life-os

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env file with your MongoDB and Todoist configurations

# 4. Start MongoDB (optional but recommended)
./scripts/start-mongodb.sh

# 5. Run Life OS
python main.py
```

### 🎯 First Use
1. **Launch Life OS**: Run `python main.py`
2. **Configure Todoist**: Set your `TODOIST_API_TOKEN` in the `.env` file to enable task management
3. **Explore News**: Select option `1` (📰 Notícias) to read latest tech news
4. **Manage Tasks**: Select option `4` (✅ Tarefas) to manage your Todoist tasks, projects, and labels
5. **Use Tools**: Try option `2` (🔧 Ferramentas) to manage MongoDB and system utilities
6. **Navigate Efficiently**: Use `M` to return to main menu from any submenu

## Project Structure
```
life-os/
├── main.py                    # Menu principal do Life OS
├── modules/                   # Módulos funcionais do sistema
│   ├── __init__.py
│   ├── news.py               # Módulo de notícias com interface completa
│   ├── tasks.py              # Módulo de tarefas integrado ao Todoist
│   └── tools.py              # Módulo de ferramentas e gerenciamento MongoDB
├── scrapers/                 # Web scrapers para diferentes sites
│   ├── __init__.py
│   └── tabnews_scraper.py    # Scraper TabNews com extração de artigos detalhados
├── utils/                    # Utilitários centrais
│   ├── __init__.py
│   ├── config.py             # Sistema de configuração centralizado
│   ├── config_manager.py     # Gerencia sites ativos/inativos
│   ├── database_manager.py   # Gerenciador MongoDB com fallbacks
│   ├── news_aggregator.py    # Agrega notícias com controle de rate limiting
│   ├── todoist_client.py     # Cliente da API do Todoist
│   └── test_connection.py    # Utilitário para testar conexões MongoDB
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
- **Rate Limiting**: Controle de 6 horas para evitar bloqueios com TTL de 5 dias
- **Interface Rica**: Navegação por páginas, seleção de artigos, retorno direto ao menu principal
- **Cache Inteligente**: Armazenamento de artigos detalhados com limpeza automática
- **Monitoramento**: Dashboard de status do banco e fontes de notícias

### 🔧 Ferramentas (Implementado)
- **Gerenciador MongoDB**: Interface completa para gerenciamento de banco de dados
- **Status de Conexão**: Monitora conectividade local vs remoto com detalhes do servidor
- **Explorador de Collections**: Lista, explora e analisa dados do MongoDB
- **Busca Avançada**: Busca por texto em documentos com resultados formatados
- **Análise de Dados**: Estatísticas de uso, tamanhos e últimas inserções
- **Interface Intuitiva**: Navegação por menus com formatação rica no terminal

### 📅 Agenda (Em breve)
- Gerenciamento de compromissos e eventos

### ✅ Tarefas (Implementado)
- **Integração Completa Todoist**: Cliente API com todas as operações CRUD
- **Gerenciamento de Tarefas**: Criar, editar, concluir e excluir tarefas
- **Prioridades e Prazos**: Definir prioridades (1-4) e datas de vencimento
- **Projetos e Organização**: Criar e gerenciar projetos com cores personalizadas
- **Sistema de Etiquetas**: Criar etiquetas e atribuir múltiplas por tarefa
- **Dashboard Analítico**: Estatísticas completas e distribuição de tarefas
- **Busca e Filtros**: Busca por texto e filtros por projeto/prioridade
- **Histórico Completo**: Visualização de tarefas concluídas com períodos
- **Export de Dados**: Exportação completa para JSON
- **Interface Rica**: Terminal UI com Rich library e navegação intuitiva

### 💰 Finanças (Implementado)
- **Gerenciamento de Contas**: Cadastro de contas correntes, poupança e investimento
- **Cartões de Crédito**: Gestão completa de cartões com bandeiras, limites e vinculação
- **Sistema de Transações**: Registro de transações com suporte a parcelamento automático
- **Compartilhamento com Alzi**: Flag "compartilhado com Alzi" para contas, cartões e transações
- **Relatório de Gastos Compartilhados**: Menu específico para transações do mês compartilhadas
- **Dashboard Financeiro**: Visão geral de saldos, limites e gastos mensais
- **Persistência Inteligente**: MongoDB com fallback JSON automático
- **CRUD Completo**: Criar, listar, editar e excluir contas, cartões e transações
- **Cálculo de Parcelamento**: Sistema automático de divisão em parcelas para cartões
- **Interface Rica**: Terminal UI com navegação intuitiva e formatação avançada

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

### Todoist Data Structures
```python
@dataclass
class TodoistTask:
    id: str                           # Unique task ID
    content: str                      # Task title/content
    description: Optional[str]        # Task description
    project_id: Optional[str]         # Associated project ID
    section_id: Optional[str]         # Section within project
    parent_id: Optional[str]          # Parent task (for subtasks)
    order: int                        # Task order
    priority: int                     # Priority level (1-4, 4=highest)
    due: Optional[Dict[str, Any]]     # Due date information
    labels: List[str]                 # Assigned labels
    is_completed: bool                # Completion status
    created_at: Optional[str]         # Creation timestamp
    assignee_id: Optional[str]        # Assignee (for shared projects)
    comment_count: int                # Number of comments
    url: Optional[str]                # Todoist web URL

@dataclass
class TodoistProject:
    id: str                           # Unique project ID
    name: str                         # Project name
    color: str                        # Project color theme
    parent_id: Optional[str]          # Parent project (for hierarchy)
    order: int                        # Project order
    comment_count: int                # Number of comments
    is_shared: bool                   # Shared project flag
    is_favorite: bool                 # Favorite status
    is_inbox_project: bool            # Inbox project flag
    is_team_inbox: bool               # Team inbox flag
    url: str                          # Todoist web URL
    view_style: str                   # View style (list/board)

@dataclass
class TodoistLabel:
    id: str                           # Unique label ID
    name: str                         # Label name
    color: str                        # Label color
    order: int                        # Label order
    is_favorite: bool                 # Favorite status
```

### Finance Data Structures
```python
@dataclass
class ContaCorrente:
    id: str                          # Unique account ID
    nome: str                        # Account name
    banco: str                       # Bank name
    agencia: str                     # Branch number
    conta: str                       # Account number
    tipo: TipoConta                  # Account type (corrente, poupanca, investimento)
    saldo_inicial: float             # Initial balance
    saldo_atual: float               # Current balance
    compartilhado_com_alzi: bool     # Shared with Alzi flag (default: False)
    ativa: bool                      # Active status
    created_at: Optional[str]        # Creation timestamp
    updated_at: Optional[str]        # Last update timestamp

@dataclass
class CartaoCredito:
    id: str                          # Unique card ID
    nome: str                        # Card name
    banco: str                       # Bank name
    bandeira: BandeiraCartao         # Card brand (visa, mastercard, elo, etc.)
    limite: float                    # Credit limit
    limite_disponivel: float         # Available limit
    conta_vinculada_id: Optional[str] # Linked checking account ID
    dia_vencimento: int              # Due date (1-31)
    dia_fechamento: int              # Closing date (1-31)
    compartilhado_com_alzi: bool     # Shared with Alzi flag (default: False)
    ativo: bool                      # Active status
    created_at: Optional[str]        # Creation timestamp
    updated_at: Optional[str]        # Last update timestamp

@dataclass
class Transacao:
    id: str                          # Unique transaction ID
    descricao: str                   # Transaction description
    valor: float                     # Transaction amount
    tipo: TipoTransacao              # Transaction type (debito/credito)
    data_transacao: str              # Transaction date
    categoria: Optional[str]         # Category
    conta_id: Optional[str]          # Associated account ID
    cartao_id: Optional[str]         # Associated card ID
    parcelamento: List[Parcelamento] # Installment details
    observacoes: Optional[str]       # Notes
    status: StatusTransacao          # Transaction status
    compartilhado_com_alzi: bool     # Shared with Alzi flag (default: False)
    created_at: Optional[str]        # Creation timestamp
    updated_at: Optional[str]        # Last update timestamp

@dataclass
class Parcelamento:
    numero_parcela: int              # Installment number
    total_parcelas: int              # Total installments
    valor_parcela: float             # Installment amount
    data_vencimento: str             # Due date
    pago: bool                       # Paid status (default: False)

@dataclass
class ResumoFinanceiro:
    total_contas: int                # Total accounts
    total_cartoes: int               # Total credit cards
    total_transacoes: int            # Total transactions (current month)
    saldo_total_contas: float        # Total balance across accounts
    limite_total_cartoes: float      # Total credit limit
    limite_disponivel_cartoes: float # Total available credit
    valor_total_gastos_mes: float    # Total expenses current month
    valor_compartilhado_alzi_mes: float # Shared expenses with Alzi current month
    contas_compartilhadas: int       # Number of shared accounts
    cartoes_compartilhados: int      # Number of shared cards
    transacoes_compartilhadas_mes: int # Number of shared transactions current month

# Enums
class TipoConta(Enum):
    CORRENTE = "corrente"            # Checking account
    POUPANCA = "poupanca"            # Savings account
    INVESTIMENTO = "investimento"    # Investment account

class BandeiraCartao(Enum):
    VISA = "visa"
    MASTERCARD = "mastercard"
    ELO = "elo"
    AMERICAN_EXPRESS = "american_express"
    HIPERCARD = "hipercard"

class TipoTransacao(Enum):
    DEBITO = "debito"               # Outgoing transaction
    CREDITO = "credito"             # Incoming transaction

class StatusTransacao(Enum):
    PENDENTE = "pendente"           # Pending
    PROCESSADA = "processada"       # Processed
    CANCELADA = "cancelada"         # Cancelled
```

### System Architecture
- **Three-Tier Persistence**: MongoDB → JSON → Memory cache
- **Rate Limiting**: Configurable update intervals (default: 6 hours)
- **Modular Design**: Easy addition of new scrapers and modules
- **Docker Integration**: Zero-config setup with automated database
- **Environment Management**: Flexible configuration via .env files
- **API Integration**: RESTful clients for external services (Todoist REST v2 + Sync v9)
- **Rich Terminal UI**: Advanced terminal interfaces with formatting and interactivity

## 🔀 Git Workflow - REGRAS IMPORTANTES

⚠️ **REGRA CRÍTICA**: NUNCA fazer push direto na branch main!

### Workflow Obrigatório para Mudanças

#### 1. Sempre criar uma nova branch para mudanças
```bash
# Criar nova branch antes de qualquer alteração
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

#### 2. Fazer commit na branch
```bash
git add .
git commit -m "sua mensagem de commit"
```

#### 3. Fazer push da branch (não da main)
```bash
git push origin nome-da-branch
```

#### 4. Criar Pull Request
- Usar GitHub interface ou `gh pr create`
- Fazer merge via Pull Request, não push direto

### Exemplos de Nomes de Branch
- `feature/todoist-api-fix` - Para novas funcionalidades
- `fix/completed-tasks-endpoint` - Para correções de bugs
- `docs/update-readme` - Para atualizações de documentação
- `refactor/database-client` - Para refatorações

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

# Testar apenas o módulo de ferramentas
python modules/tools.py

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

# Testar conexão MongoDB (local ou remoto)
python utils/test_connection.py "mongodb://user:pass@host:port/database"

# Testar funcionalidades do gerenciador MongoDB
python -c "
from modules.tools import MongoDBTool
tool = MongoDBTool()
tool.show_connection_status()
tool.list_collections()
"
### 🧪 Testes e Desenvolvimento - Módulo de Tarefas
```bash
# Testar apenas o módulo de tarefas
python modules/tasks.py

# Testar cliente Todoist básico
python -c "
from utils.todoist_client import TodoistClient
from utils.config import Config
client = TodoistClient(Config.TODOIST_API_TOKEN)
projects = client.get_projects()
print(f'Projetos: {len(projects)}')
for p in projects[:3]:
    print(f'  - {p.name}')
"

# Testar criação de tarefa
python -c "
from utils.todoist_client import TodoistClient
from utils.config import Config
client = TodoistClient(Config.TODOIST_API_TOKEN)
task = client.create_task('Teste via API', priority=3)
if task:
    print(f'Tarefa criada: {task.content} (ID: {task.id})')
    client.complete_task(task.id)
    print('Tarefa marcada como concluída')
"

# Testar tarefas concluídas (corrigido - usa Sync API v9)
python -c "
from utils.todoist_client import TodoistClient
from utils.config import Config
client = TodoistClient(Config.TODOIST_API_TOKEN)
completed = client.get_completed_tasks(limit=5)
print(f'Tarefas concluídas: {len(completed)}')
for task in completed[:3]:
    print(f'  ✓ {task.get(\"content\", task.get(\"item\", {}).get(\"content\", \"Sem título\"))}')
"

# Testar funcionalidades do módulo de tarefas
python -c "
from modules.tasks import TasksModule
module = TasksModule()
if module.client:
    tasks = module.client.get_tasks()
    projects = module.client.get_projects()
    labels = module.client.get_labels()
    print(f'Status: {len(tasks)} tarefas, {len(projects)} projetos, {len(labels)} etiquetas')
"

# Testar configuração do Todoist
python -c "
from utils.config import Config
token = Config.TODOIST_API_TOKEN
print(f'Token configurado: {\"Sim\" if token else \"Não\"}')
if token:
    print(f'Token: {token[:10]}...{token[-4:]}')
"
```

## 🔧 Configuração do Módulo de Tarefas

### Obter Token da API Todoist
1. **Acesse**: [Todoist Settings > Integrations](https://todoist.com/prefs/integrations)
2. **Copie o API Token**
3. **Configure no .env**:
```bash
TODOIST_API_TOKEN=your_token_here
```

### Recursos Disponíveis

#### 📝 Gerenciamento de Tarefas
- **CRUD Completo**: Create, Read, Update, Delete
- **Prioridades**: 4 níveis (Baixa → Urgente)
- **Datas**: Linguagem natural ("hoje", "amanhã", "próxima sexta")
- **Etiquetas**: Múltiplas etiquetas por tarefa
- **Projetos**: Organização hierárquica
- **Descrições**: Texto livre para detalhes

#### 📁 Gerenciamento de Projetos
- **Criação/Edição**: Nomes, cores, favoritos
- **Estatísticas**: Análise de tarefas por projeto
- **Organização**: Hierarquia de projetos
- **Cores Personalizadas**: 20 opções de cores

#### 🏷️ Sistema de Etiquetas
- **Criação Dinâmica**: Novas etiquetas conforme necessário
- **Cores**: Personalização visual
- **Atribuição**: Múltiplas etiquetas por tarefa
- **Filtros**: Busca por etiquetas específicas

#### 📊 Dashboard e Analytics
- **Visão Geral**: Distribuição de tarefas por status
- **Métricas**: Produtividade e conclusões
- **Gráficos**: Representação visual de dados
- **Tendências**: Análise temporal

#### 🔍 Busca e Filtros
- **Busca Textual**: Conteúdo, descrição, etiquetas
- **Filtros**: Projeto, prioridade, data
- **Histórico**: Tarefas concluídas por período
- **Exportação**: Dados em formato JSON

### Comandos de Uso Direto
```bash
# Acesso rápido ao módulo de tarefas
python main.py  # Depois selecionar opção 4

# Teste de conectividade
python -c "
from modules.tasks import TasksModule
app = TasksModule()
print('Módulo de tarefas:', 'OK' if app.client else 'Token não configurado')
"
```

### 🧪 Testes e Desenvolvimento - Módulo de Finanças
```bash
# Testar apenas o módulo de finanças
python modules/finances.py

# Testar cliente de finanças básico
python -c "
from utils.finance_client import FinanceClient
client = FinanceClient()
resumo = client.obter_resumo_financeiro()
print(f'Resumo: {resumo.total_contas} contas, {resumo.total_cartoes} cartões')
"

# Testar criação de conta corrente
python -c "
from utils.finance_client import FinanceClient
from utils.finance_models import TipoConta
client = FinanceClient()
conta = client.criar_conta(
    nome='Conta Teste',
    banco='Banco Teste',
    agencia='1234',
    conta='56789-0',
    tipo=TipoConta.CORRENTE,
    saldo_inicial=1000.0,
    compartilhado_com_alzi=True
)
if conta:
    print(f'Conta criada: {conta.nome} (ID: {conta.id[:8]}...)')
    # Limpar teste
    client.excluir_conta(conta.id)
    print('Conta de teste removida')
"

# Testar criação de cartão de crédito
python -c "
from utils.finance_client import FinanceClient
from utils.finance_models import BandeiraCartao
client = FinanceClient()
cartao = client.criar_cartao(
    nome='Cartão Teste',
    banco='Banco Teste',
    bandeira=BandeiraCartao.VISA,
    limite=5000.0,
    dia_vencimento=10,
    dia_fechamento=5,
    compartilhado_com_alzi=True
)
if cartao:
    print(f'Cartão criado: {cartao.nome} (ID: {cartao.id[:8]}...)')
    # Limpar teste
    client.excluir_cartao(cartao.id)
    print('Cartão de teste removido')
"

# Testar transação com parcelamento
python -c "
from utils.finance_client import FinanceClient
from utils.finance_models import TipoTransacao
from datetime import datetime
client = FinanceClient()

# Criar conta temporária
conta = client.criar_conta('Conta Temp', 'Banco', '1', '1', 'corrente', 1000)
if conta:
    # Criar transação parcelada
    transacao = client.criar_transacao(
        descricao='Compra Teste Parcelada',
        valor=300.0,
        tipo=TipoTransacao.DEBITO,
        data_transacao=datetime.now().isoformat(),
        categoria='Teste',
        conta_id=conta.id,
        parcelas=3,
        compartilhado_com_alzi=True
    )
    if transacao:
        print(f'Transação criada: {transacao.descricao}')
        print(f'Parcelamento: {len(transacao.parcelamento)} parcelas')
        for i, parcela in enumerate(transacao.parcelamento, 1):
            print(f'  Parcela {i}: R$ {parcela.valor_parcela:.2f} - {parcela.data_vencimento[:10]}')
        
        # Limpar teste
        client.excluir_transacao(transacao.id)
        client.excluir_conta(conta.id)
        print('Dados de teste removidos')
"

# Testar funcionalidades do módulo de finanças
python -c "
from modules.finances import FinancesModule
module = FinancesModule()
if module.client:
    contas = module.client.listar_contas()
    cartoes = module.client.listar_cartoes()
    print(f'Status: {len(contas)} contas, {len(cartoes)} cartões')
    
    # Testar transações compartilhadas do mês
    from datetime import datetime
    hoje = datetime.now()
    compartilhadas = module.client.obter_transacoes_mes(hoje.year, hoje.month, True)
    print(f'Transações compartilhadas este mês: {len(compartilhadas)}')
"

# Testar conexão do banco de dados
python -c "
from utils.finance_client import FinanceClient
client = FinanceClient()
connected = client.db_manager.is_connected()
print(f'Banco conectado: {\"Sim\" if connected else \"Não (usando fallback JSON)\"}')
if connected:
    print(f'Database: {client.db_manager.db_name}')
"
```

## 💰 Configuração do Módulo de Finanças

### Funcionalidades Principais

#### 🏦 Gerenciamento de Contas
- **Tipos Suportados**: Corrente, Poupança, Investimento
- **Dados Completos**: Nome, banco, agência, conta, saldos
- **Flag Alzi**: Marcar contas compartilhadas com Alzi
- **Status**: Ativar/desativar contas
- **Histórico**: Timestamps de criação e atualização

#### 💳 Gerenciamento de Cartões
- **Bandeiras**: Visa, Mastercard, Elo, American Express, Hipercard
- **Limites**: Controle de limite total e disponível
- **Vinculação**: Associar cartões a contas correntes
- **Datas**: Vencimento e fechamento da fatura
- **Flag Alzi**: Marcar cartões compartilhados

#### 📝 Sistema de Transações
- **Tipos**: Débito (saída) e Crédito (entrada)
- **Parcelamento**: Automático para cartões de crédito
- **Categorização**: Sistema flexível de categorias
- **Múltiplas Origens**: Contas ou cartões
- **Flag Alzi**: Marcar transações compartilhadas
- **Status**: Pendente, processada, cancelada

#### 👫 Relatório Alzi
- **Visão Mensal**: Transações compartilhadas do mês atual
- **Cálculo Automático**: Valor total e valor dividido (50%)
- **Detalhamento**: Lista completa de gastos compartilhados
- **Categorização**: Organização por categoria de gasto

### Comandos de Uso Direto
```bash
# Acesso rápido ao módulo de finanças
python main.py  # Depois selecionar opção 6

# Teste de conectividade
python -c "
from modules.finances import FinancesModule
app = FinancesModule()
print('Módulo de finanças:', 'OK' if app.client else 'Erro na inicialização')
"
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
- **Full Article View**: Read complete articles within the terminal with instant loading
- **Markdown Formatting**: Proper text formatting with headers, lists, quotes
- **Comment System**: View all article comments with 89% extraction rate and duplicate filtering
- **Interactive Navigation**: Easy switching between content and comments with 'M' shortcut
- **Smart Caching**: Instant article loading from cache with 6-hour update intervals

**💾 Intelligent Persistence**
- **MongoDB Integration**: Production-ready database with indexes and TTL cleanup
- **Automatic Fallback**: Seamless fallback to JSON when DB unavailable
- **Data Consistency**: Maintain article history and reading state with cache invalidation
- **Performance Optimization**: Smart caching with 6-hour updates and 5-day TTL
- **Article Details Cache**: Dedicated collection for full article content with automatic cleanup

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

# Integração Todoist
TODOIST_API_TOKEN=your_todoist_api_token_here
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

## 🔧 Usando o Módulo de Ferramentas

### Acesso ao Gerenciador MongoDB
```bash
# 1. Executar Life OS
python main.py

# 2. Selecionar opção 2 (🔧 Ferramentas)
# 3. Selecionar opção 1 (🗄️ Gerenciador MongoDB)
```

### Funcionalidades Disponíveis

**📊 Status da Conexão (Opção 1)**
- Verifica se MongoDB está conectado (local ou remoto)
- Mostra host, porta, database e versão do MongoDB
- Identifica automaticamente se está usando configuração local ou remota

**📁 Listar Collections (Opção 2)**
- Lista todas as collections do banco de dados
- Mostra quantidade de documentos em cada collection
- Exibe tamanho aproximado de cada collection

**🔍 Detalhes de Collection (Opção 3)**
- Estatísticas detalhadas de uma collection específica
- Informações sobre índices e tamanhos
- Exibe exemplos dos primeiros documentos
- Mostra data do último documento inserido

**🔎 Buscar Documentos (Opção 4)**
- Busca por texto em campos como título, conteúdo, autor, link
- Busca case-insensitive com regex
- Limita resultados para evitar overload
- Exibe resultados formatados com syntax highlighting

**⏰ Documentos Recentes (Opção 5)**
- Mostra os documentos mais recentemente inseridos
- Útil para verificar atualizações do sistema
- Ordenação por ObjectId (timestamp de criação)

### Exemplos de Uso Direto
```bash
# Testar status de conexão
python -c "
from modules.tools import MongoDBTool
tool = MongoDBTool()
tool.show_connection_status()
"

# Listar todas as collections
python -c "
from modules.tools import MongoDBTool
tool = MongoDBTool()
tool.list_collections()
"

# Buscar artigos sobre 'API'
python -c "
from modules.tools import MongoDBTool
tool = MongoDBTool()
tool.search_documents('news_articles', 'API', 5)
"

# Ver documentos recentes
python -c "
from modules.tools import MongoDBTool
tool = MongoDBTool()
tool.recent_documents('news_articles', 3)
"
```

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