#!/bin/bash

# Script para iniciar MongoDB com Docker Compose
echo "🚀 Iniciando MongoDB para Life OS..."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verificar se docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Por favor, instale o Docker Compose."
    exit 1
fi

# Ir para o diretório do projeto
cd "$(dirname "$0")/.."

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Você pode editá-lo se necessário."
fi

# Iniciar containers
echo "🐳 Iniciando containers MongoDB..."
docker-compose up -d mongodb

# Aguardar MongoDB estar pronto
echo "⏳ Aguardando MongoDB estar pronto..."
sleep 10

# Verificar se está funcionando
if docker-compose ps mongodb | grep -q "Up"; then
    echo "✅ MongoDB iniciado com sucesso!"
    echo ""
    echo "📊 Informações do MongoDB:"
    echo "   Host: localhost:27017"
    echo "   Database: lifeos"
    echo "   Username: lifeos_app"
    echo "   Password: lifeos_app_password"
    echo ""
    echo "🌐 Mongo Express (Interface Web):"
    echo "   Iniciando Mongo Express..."
    docker-compose up -d mongo-express
    sleep 5
    if docker-compose ps mongo-express | grep -q "Up"; then
        echo "   ✅ Disponível em: http://localhost:8081"
    else
        echo "   ⚠️  Mongo Express não conseguiu iniciar"
    fi
    echo ""
    echo "🔧 Para parar os serviços: ./scripts/stop-mongodb.sh"
else
    echo "❌ Falha ao iniciar MongoDB"
    echo "📋 Logs do container:"
    docker-compose logs mongodb
    exit 1
fi