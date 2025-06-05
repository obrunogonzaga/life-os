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
        
        # Mostrar modo do banco selecionado
        database_mode = os.getenv("DATABASE_MODE", "local")
        if database_mode == "remote":
            print(f"🌐 Modo: Banco de dados REMOTO (Coolify/Hostinger)")
        else:
            print(f"🏠 Modo: Banco de dados LOCAL (Docker)")
    else:
        # Tentar carregar .env.example como fallback para desenvolvimento
        env_example = current_dir / '.env.example'
        if env_example.exists():
            print(f"⚠️  Arquivo .env não encontrado. Usando configurações padrão (LOCAL).")
            print(f"   Copie {env_example} para .env e ajuste as configurações.")
            print(f"   Para usar MongoDB remoto, configure DATABASE_MODE=remote no .env")


# Carregar variáveis de ambiente na importação
load_environment()


class Config:
    """
    Classe para acessar configurações do sistema
    """
    
    # Database Mode Selection
    DATABASE_MODE = os.getenv("DATABASE_MODE", "local")  # local | remote
    
    # MongoDB Configuration - Local
    MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "lifeos")
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    
    # MongoDB Configuration - Remote
    REMOTE_MONGODB_HOST = os.getenv("REMOTE_MONGODB_HOST")
    REMOTE_MONGODB_PORT = int(os.getenv("REMOTE_MONGODB_PORT", "27017"))
    REMOTE_MONGODB_DATABASE = os.getenv("REMOTE_MONGODB_DATABASE", "lifeos")
    REMOTE_MONGODB_USERNAME = os.getenv("REMOTE_MONGODB_USERNAME")
    REMOTE_MONGODB_PASSWORD = os.getenv("REMOTE_MONGODB_PASSWORD")
    REMOTE_MONGODB_URI = os.getenv("REMOTE_MONGODB_URI")  # Full URI if needed
    
    # Admin credentials (local only)
    MONGODB_ADMIN_USERNAME = os.getenv("MONGODB_ADMIN_USERNAME", "lifeos")
    MONGODB_ADMIN_PASSWORD = os.getenv("MONGODB_ADMIN_PASSWORD", "lifeos123")
    
    # Application Settings
    NEWS_UPDATE_INTERVAL_HOURS = int(os.getenv("NEWS_UPDATE_INTERVAL_HOURS", "6"))
    MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50"))
    
    # Todoist Integration
    TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
    
    # Development Settings
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_remote_config(cls) -> bool:
        """
        Valida se a configuração remota está completa
        """
        if cls.DATABASE_MODE != "remote":
            return True
        
        # Se há URI completa, validar ela
        if cls.REMOTE_MONGODB_URI:
            return cls.REMOTE_MONGODB_URI.startswith("mongodb://") or cls.REMOTE_MONGODB_URI.startswith("mongodb+srv://")
        
        # Senão, validar componentes individuais
        required_fields = [
            cls.REMOTE_MONGODB_HOST,
            cls.REMOTE_MONGODB_USERNAME,
            cls.REMOTE_MONGODB_PASSWORD
        ]
        
        return all(field for field in required_fields)
    
    @classmethod
    def get_mongodb_connection_string(cls) -> str:
        """
        Retorna string de conexão MongoDB baseada nas configurações (local ou remoto)
        """
        from urllib.parse import quote_plus
        
        if cls.DATABASE_MODE == "remote":
            # Usar configuração remota (Coolify/Hostinger)
            
            # Se houver URI completa, usar ela
            if cls.REMOTE_MONGODB_URI:
                return cls.REMOTE_MONGODB_URI
            
            # Senão, construir URI a partir dos componentes
            if cls.REMOTE_MONGODB_USERNAME and cls.REMOTE_MONGODB_PASSWORD and cls.REMOTE_MONGODB_HOST:
                username_encoded = quote_plus(cls.REMOTE_MONGODB_USERNAME)
                password_encoded = quote_plus(cls.REMOTE_MONGODB_PASSWORD)
                return f"mongodb://{username_encoded}:{password_encoded}@{cls.REMOTE_MONGODB_HOST}:{cls.REMOTE_MONGODB_PORT}/{cls.REMOTE_MONGODB_DATABASE}?authSource={cls.REMOTE_MONGODB_DATABASE}"
            else:
                print("⚠️ Configuração remota incompleta. Verifique REMOTE_MONGODB_* no .env")
                print("📄 Necessário: REMOTE_MONGODB_HOST, REMOTE_MONGODB_USERNAME, REMOTE_MONGODB_PASSWORD")
                # Fallback para local
                return cls._get_local_connection_string()
        else:
            # Usar configuração local
            return cls._get_local_connection_string()
    
    @classmethod
    def _get_local_connection_string(cls) -> str:
        """
        Retorna string de conexão MongoDB local
        """
        if cls.MONGODB_USERNAME and cls.MONGODB_PASSWORD:
            from urllib.parse import quote_plus
            username_encoded = quote_plus(cls.MONGODB_USERNAME)
            password_encoded = quote_plus(cls.MONGODB_PASSWORD)
            return f"mongodb://{username_encoded}:{password_encoded}@{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/{cls.MONGODB_DATABASE}?authSource={cls.MONGODB_DATABASE}"
        else:
            return f"mongodb://{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/"
    
    @classmethod
    def print_config(cls):
        """
        Imprime configuração atual (sem senhas)
        """
        print("\n📋 Configuração atual do Life OS:")
        print(f"   🎯 Modo do Banco: {cls.DATABASE_MODE.upper()}")
        
        if cls.DATABASE_MODE == "remote":
            print(f"   🌐 MongoDB Remoto:")
            print(f"      Host: {cls.REMOTE_MONGODB_HOST or 'NÃO CONFIGURADO'}:{cls.REMOTE_MONGODB_PORT}")
            print(f"      Database: {cls.REMOTE_MONGODB_DATABASE}")
            print(f"      Auth: {'✅ Sim' if cls.REMOTE_MONGODB_USERNAME else '❌ Não configurado'}")
            if cls.REMOTE_MONGODB_URI:
                print(f"      URI Customizada: {'✅ Configurada' if cls.REMOTE_MONGODB_URI else '❌ Não'}")
        else:
            print(f"   🏠 MongoDB Local:")
            print(f"      Host: {cls.MONGODB_HOST}:{cls.MONGODB_PORT}")
            print(f"      Database: {cls.MONGODB_DATABASE}")
            print(f"      Auth: {'✅ Sim' if cls.MONGODB_USERNAME else '❌ Não'}")
        
        print(f"   ⚙️ Configurações da Aplicação:")
        print(f"      Intervalo de atualização: {cls.NEWS_UPDATE_INTERVAL_HOURS}h")
        print(f"      Max artigos por fonte: {cls.MAX_ARTICLES_PER_SOURCE}")
        print(f"      Todoist Token: {'✅ Configurado' if cls.TODOIST_API_TOKEN else '❌ Não configurado'}")
        print(f"      Debug Mode: {'✅ Sim' if cls.DEBUG else '❌ Não'}")
        print()
    
    @classmethod
    def get_current_database_info(cls) -> dict:
        """
        Retorna informações sobre a configuração atual do banco
        """
        if cls.DATABASE_MODE == "remote":
            return {
                "mode": "remote",
                "host": cls.REMOTE_MONGODB_HOST,
                "port": cls.REMOTE_MONGODB_PORT,
                "database": cls.REMOTE_MONGODB_DATABASE,
                "has_auth": bool(cls.REMOTE_MONGODB_USERNAME and cls.REMOTE_MONGODB_PASSWORD),
                "connection_string": cls.get_mongodb_connection_string(),
                "is_valid": cls.validate_remote_config()
            }
        else:
            return {
                "mode": "local",
                "host": cls.MONGODB_HOST,
                "port": cls.MONGODB_PORT,
                "database": cls.MONGODB_DATABASE,
                "has_auth": bool(cls.MONGODB_USERNAME and cls.MONGODB_PASSWORD),
                "connection_string": cls.get_mongodb_connection_string(),
                "is_valid": True
            }