# 🌐 Configuração MongoDB Remoto - Coolify/Hostinger

Este guia explica como configurar o Life OS para usar um MongoDB remoto hospedado no Hostinger via Coolify.

## 🎯 Vantagens do MongoDB Remoto

- 📱 **Acesso universal**: Mesmos dados em qualquer dispositivo/local
- 🔄 **Sincronização automática**: Sem necessidade de sincronizar dados manualmente
- ☁️ **Backup em nuvem**: Dados seguros e disponíveis 24/7
- 🚀 **Performance**: Servidor dedicado com recursos garantidos
- 🔒 **Segurança**: Configuração profissional com autenticação

## 📋 Pré-requisitos

- Conta no Hostinger com VPS ou Cloud hosting
- Coolify instalado e configurado no seu servidor
- Acesso ao painel Coolify
- Arquivo `.env` local para configuração

## 🛠️ Passo 1: Configuração no Coolify

### 1.1 Acessar o Painel Coolify
```bash
# Acesse seu painel Coolify
https://seu-dominio.com:8000
# ou conforme sua configuração
```

### 1.2 Criar Novo Database Service
1. **Navegue para Databases** → **New Database**
2. **Selecione MongoDB**
3. **Configure os parâmetros:**

```yaml
Database Configuration:
  Name: lifeos-mongodb
  Database Name: lifeos
  Username: lifeos_user
  Password: [generate-strong-password]
  Port: 27017
  Memory: 1GB (ou conforme seu plano)
  Storage: 10GB (ou conforme necessário)
```

### 1.3 Configurar Acesso Externo
```yaml
Network Settings:
  External Access: ✅ Enable
  Port Mapping: 27017:27017
  Allowed IPs: [seu-ip-ou-0.0.0.0/0-para-acesso-global]
```

### 1.4 Deploy e Anotar Informações
```bash
# Após o deploy, anote:
Host: seu-servidor.hostinger.com (ou IP)
Port: 27017
Database: lifeos
Username: lifeos_user
Password: [sua-senha-gerada]
```

## ⚙️ Passo 2: Configuração Local

### 2.1 Atualizar .env
```bash
# Copie .env.example para .env se ainda não existe
cp .env.example .env

# Edite o .env com suas configurações
nano .env
```

### 2.2 Configurar Variáveis de Ambiente
```bash
# Database Mode Selection
DATABASE_MODE=remote

# MongoDB Configuration - Local Development (manter para fallback)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=lifeos
MONGODB_USERNAME=lifeos_app
MONGODB_PASSWORD=lifeos_app_password

# MongoDB Configuration - Remote (Coolify/Hostinger)
REMOTE_MONGODB_HOST=seu-servidor.hostinger.com
REMOTE_MONGODB_PORT=27017
REMOTE_MONGODB_DATABASE=lifeos
REMOTE_MONGODB_USERNAME=lifeos_user
REMOTE_MONGODB_PASSWORD=sua-senha-super-segura

# Optional: URI completa (se preferir)
# REMOTE_MONGODB_URI=mongodb://lifeos_user:sua-senha@seu-servidor.hostinger.com:27017/lifeos?authSource=lifeos

# Application Settings
NEWS_UPDATE_INTERVAL_HOURS=6
MAX_ARTICLES_PER_SOURCE=50
DEBUG=false
LOG_LEVEL=INFO
```

## 🔧 Passo 3: Teste da Configuração

### 3.1 Verificar Configuração
```bash
# Teste a configuração
python -c "from utils.config import Config; Config.print_config()"
```

**Output esperado:**
```
📋 Configuração atual do Life OS:
   🎯 Modo do Banco: REMOTE
   🌐 MongoDB Remoto:
      Host: seu-servidor.hostinger.com:27017
      Database: lifeos
      Auth: ✅ Sim
   ⚙️ Configurações da Aplicação:
      Intervalo de atualização: 6h
      Max artigos por fonte: 50
      Debug Mode: ❌ Não
```

### 3.2 Teste de Conexão
```bash
# Teste conexão com o MongoDB remoto
python -c "
from utils.database_manager import DatabaseManager
from utils.config import Config

print('Testando conexão...')
db = DatabaseManager()
if db.is_connected():
    print('✅ Conexão remota bem-sucedida!')
    print(f'🌐 Conectado em: {Config.REMOTE_MONGODB_HOST}')
else:
    print('❌ Falha na conexão remota')
    print('🔄 Sistema usará fallback JSON')
"
```

### 3.3 Executar Life OS
```bash
# Execute o Life OS normalmente
python main.py
```

## 🔄 Passo 4: Migração de Dados (Opcional)

Se você já tem dados locais e quer migrá-los:

### 4.1 Backup Local
```bash
# Backup dos dados JSON locais
cp data/news_cache.json data/news_cache_backup.json
cp data/article_details_cache.json data/article_details_backup.json
```

### 4.2 Executar Migração
```bash
# Force update para popular o MongoDB remoto
python -c "
from utils.news_aggregator import NewsAggregator
from utils.config_manager import ConfigManager

config = ConfigManager()
news = NewsAggregator(config)
print('🔄 Forçando atualização para popular MongoDB remoto...')
news.force_update_all()
print('✅ Migração concluída!')
"
```

## 🚨 Troubleshooting

### Problema: Conexão Recusada
```bash
# Verificar se o MongoDB está rodando no Coolify
# Via painel Coolify: Services → lifeos-mongodb → Status

# Testar conectividade de rede
telnet seu-servidor.hostinger.com 27017
```

### Problema: Autenticação Falhando
```bash
# Verificar credenciais no painel Coolify
# Databases → lifeos-mongodb → Environment Variables

# Testar credenciais manualmente
mongo mongodb://lifeos_user:sua-senha@seu-servidor.hostinger.com:27017/lifeos
```

### Problema: Firewall Bloqueando
```bash
# No servidor Hostinger, verificar firewall
sudo ufw status
sudo ufw allow 27017

# Ou configurar via painel Hostinger
```

## 🔄 Alternando Entre Local e Remoto

### Para usar Local:
```bash
# No .env
DATABASE_MODE=local
```

### Para usar Remoto:
```bash
# No .env
DATABASE_MODE=remote
```

### Verificar modo atual:
```bash
python -c "from utils.config import Config; print(f'Modo atual: {Config.DATABASE_MODE}')"
```

## 🛡️ Segurança

### Recomendações:
1. **Senha forte**: Use senhas complexas (mínimo 16 caracteres)
2. **IP restrito**: Configure acesso apenas do seu IP se possível
3. **SSL/TLS**: Configure conexão criptografada se disponível
4. **Backup regular**: Configure backup automático no Coolify
5. **Monitoramento**: Ative logs e monitoramento

### Configuração SSL (Avançado):
```bash
# Se seu Coolify suporta SSL para MongoDB
REMOTE_MONGODB_URI=mongodb://lifeos_user:senha@servidor:27017/lifeos?ssl=true&authSource=lifeos
```

## 📊 Monitoramento

### Via Coolify:
- **Logs**: Services → lifeos-mongodb → Logs
- **Métricas**: Resources → Memory/CPU usage
- **Status**: Dashboard → Services status

### Via Life OS:
```bash
# Estatísticas do banco
python main.py
# → Módulo Notícias → Opção 6 (Estatísticas)
```

## 🎉 Pronto!

Seu Life OS agora está configurado com MongoDB remoto no Hostinger via Coolify!

### Benefícios ativados:
- ✅ Acesso aos dados de qualquer lugar
- ✅ Backup automático em nuvem
- ✅ Performance de servidor dedicado
- ✅ Fallback automático para JSON se necessário
- ✅ Sincronização instantânea entre dispositivos

---

## 📞 Suporte

**Problemas?** Verifique:
1. Configuração do .env
2. Status do serviço no Coolify
3. Conectividade de rede
4. Logs do Life OS com DEBUG=true