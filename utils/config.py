#!/usr/bin/env python3
"""
Configurações centralizadas do Life OS
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """
    Carrega variáveis de ambiente do arquivo .env se existir
    """
    # Encontrar o diretório raiz do projeto
    current_dir = Path(__file__).parent.parent
    env_file = current_dir / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Variáveis de ambiente carregadas de {env_file}")
    else:
        # Tentar carregar .env.example como fallback para desenvolvimento
        env_example = current_dir / '.env.example'
        if env_example.exists():
            print(f"⚠️  Arquivo .env não encontrado. Usando configurações padrão.")
            print(f"   Copie {env_example} para .env e ajuste as configurações.")


# Carregar variáveis de ambiente na importação
load_environment()


class Config:
    """
    Classe para acessar configurações do sistema
    """
    
    # MongoDB Configuration
    MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "lifeos")
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    
    # Admin credentials
    MONGODB_ADMIN_USERNAME = os.getenv("MONGODB_ADMIN_USERNAME", "lifeos")
    MONGODB_ADMIN_PASSWORD = os.getenv("MONGODB_ADMIN_PASSWORD", "lifeos123")
    
    # Application Settings
    NEWS_UPDATE_INTERVAL_HOURS = int(os.getenv("NEWS_UPDATE_INTERVAL_HOURS", "6"))
    MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50"))
    
    # Development Settings
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_mongodb_connection_string(cls) -> str:
        """
        Retorna string de conexão MongoDB baseada nas configurações
        """
        if cls.MONGODB_USERNAME and cls.MONGODB_PASSWORD:
            from urllib.parse import quote_plus
            username_encoded = quote_plus(cls.MONGODB_USERNAME)
            password_encoded = quote_plus(cls.MONGODB_PASSWORD)
            # Especificar authSource para autenticação no banco correto
            return f"mongodb://{username_encoded}:{password_encoded}@{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/{cls.MONGODB_DATABASE}?authSource={cls.MONGODB_DATABASE}"
        else:
            return f"mongodb://{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/"
    
    @classmethod
    def print_config(cls):
        """
        Imprime configuração atual (sem senhas)
        """
        print("\n📋 Configuração atual do Life OS:")
        print(f"   MongoDB Host: {cls.MONGODB_HOST}:{cls.MONGODB_PORT}")
        print(f"   MongoDB Database: {cls.MONGODB_DATABASE}")
        print(f"   MongoDB Auth: {'✅ Sim' if cls.MONGODB_USERNAME else '❌ Não'}")
        print(f"   Intervalo de atualização: {cls.NEWS_UPDATE_INTERVAL_HOURS}h")
        print(f"   Max artigos por fonte: {cls.MAX_ARTICLES_PER_SOURCE}")
        print(f"   Debug Mode: {'✅ Sim' if cls.DEBUG else '❌ Não'}")
        print()