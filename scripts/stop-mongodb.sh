#!/bin/bash

# Script para parar MongoDB com Docker Compose
echo "🛑 Parando MongoDB do Life OS..."

# Ir para o diretório do projeto
cd "$(dirname "$0")/.."

# Parar containers
echo "🐳 Parando containers..."
docker-compose down

echo "✅ MongoDB parado com sucesso!"
echo ""
echo "ℹ️  Para iniciar novamente: ./scripts/start-mongodb.sh"
echo "🗑️  Para remover dados permanentemente: docker-compose down -v"