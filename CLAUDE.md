# Life OS - Sistema de Organização Pessoal

## Quick Start

### ⚡ Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your MongoDB and Todoist tokens

# 3. Start MongoDB (optional)
./scripts/start-mongodb.sh

# 4. Run Life OS
python main.py
```

## Módulos Disponíveis

### 📰 Notícias (Implementado)
- Agregador de notícias tech (TabNews)
- Cache inteligente com MongoDB/JSON fallback
- Interface rica com navegação por artigos

### 🔧 Ferramentas (Implementado)  
- Gerenciador MongoDB completo
- Status de conexão e explorador de collections
- Busca avançada e análise de dados

### ✅ Tarefas (Implementado)
- Integração completa com Todoist API
- CRUD de tarefas, projetos e etiquetas
- Dashboard analítico e exportação

### 💰 Finanças (Implementado - DDD Architecture)
- **Arquitetura DDD**: Domain, Service e UI layers
- **Contas**: CRUD completo (corrente, poupança, investimento) 
- **Cartões**: Gestão com limites, faturas e vinculação
- **Transações**: Sistema com parcelamento automático
- **Alzi**: Compartilhamento de gastos com relatórios
- **Dashboard**: Análises detalhadas e resumos
- **Testes**: 2,549 linhas de código de teste

## Comandos Essenciais

### 🚀 Execução
```bash
# Iniciar Life OS
python main.py

# Testes do módulo de finanças
python tests/run_services_tests.py

# Testar conexão MongoDB
python utils/test_connection.py
```

### 🧪 Testes Rápidos
```bash
# Testar módulo de notícias
python modules/news.py

# Testar módulo de tarefas  
python modules/tasks.py

# Testar listagem de transações
python -c "
from modules.finances.services.transaction_service import TransactionService
from utils.database_manager import DatabaseManager
service = TransactionService(DatabaseManager())
print(f'Transações: {len(service.list_transactions())}')
"
```

## Configuração

### 🔧 Variáveis de Ambiente (.env)
```bash
# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=lifeos
MONGODB_USERNAME=lifeos_app
MONGODB_PASSWORD=lifeos_app_password

# APIs
TODOIST_API_TOKEN=your_token_here

# Config
NEWS_UPDATE_INTERVAL_HOURS=6
```

### 📊 MongoDB Setup
```bash
# Docker (recomendado)
./scripts/start-mongodb.sh   # Inicia containers
./scripts/stop-mongodb.sh    # Para containers

# Interface web: http://localhost:8081
```

## 🔀 Git Workflow

⚠️ **NUNCA fazer push direto na main!**

```bash
# 1. Criar branch
git checkout -b feature/nome-da-feature

# 2. Fazer commit
git add .
git commit -m "sua mensagem"

# 3. Push da branch
git push origin nome-da-branch

# 4. Criar Pull Request
```

## Sistema de Fallback
- **MongoDB** → **JSON** → **Memory**
- Funciona sempre, independente da configuração
- Cache automático com TTL configurável

## Arquitetura - Módulo de Finanças

```
modules/finances/
├── domains/          # Lógica de negócios + Data access
├── services/         # Orquestração de operações
└── ui/              # Interface e apresentação
```

- **Domain Layer**: 7 domain classes com regras de negócio
- **Service Layer**: 6 services principais (Account, Card, Transaction, etc.)  
- **UI Layer**: 8 componentes modulares especializados
- **Cobertura**: 100% testado com runner personalizado

## Troubleshooting

### MongoDB Issues
```bash
# Verificar containers
docker ps | grep lifeos-mongodb

# Reiniciar
./scripts/stop-mongodb.sh && ./scripts/start-mongodb.sh

# Logs
docker-compose logs mongodb
```

### Dependencies
```bash
# Reinstalar
pip install --force-reinstall -r requirements.txt
```

### Permissões
```bash
# Scripts executáveis
chmod +x scripts/*.sh
```

## Current Status
- ✅ **Notícias**: Funcional com cache inteligente
- ✅ **Tarefas**: Integração Todoist completa  
- ✅ **Ferramentas**: MongoDB manager completo
- ✅ **Finanças**: Arquitetura DDD 100% implementada
- 🔄 **Agenda**: Em desenvolvimento
- 🔄 **Notas**: Planejado
- 🔄 **Hábitos**: Planejado