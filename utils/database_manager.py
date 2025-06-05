#!/usr/bin/env python3
"""
Gerenciador de banco de dados MongoDB para o Life OS
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import json
from urllib.parse import quote_plus
from utils.config import Config


class DatabaseManager:
    """
    Gerenciador de conexão e operações do MongoDB para o Life OS
    """
    
    def __init__(self, connection_string: str = None):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            connection_string: String de conexão do MongoDB. Se None, usa configuração.
        """
        if connection_string is None:
            connection_string = Config.get_mongodb_connection_string()
        
        self.connection_string = connection_string
        self.client = None
        self.db = None
        self.connected = False
        
        # Nome do banco de dados
        self.db_name = Config.MONGODB_DATABASE
        
        # Tentar conectar na inicialização
        self.connect()
    
    def connect(self) -> bool:
        """
        Estabelece conexão com o MongoDB
        
        Returns:
            bool: True se conexão bem-sucedida, False caso contrário
        """
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=3000,  # 3 segundos de timeout
                connectTimeoutMS=3000
            )
            
            # Testar a conexão básica
            self.client.admin.command('ping')
            
            # Selecionar banco de dados
            self.db = self.client[self.db_name]
            
            # Testar se podemos fazer operações no banco (verificar autenticação)
            try:
                # Tentar uma operação simples que requer permissões
                self.db.test_collection.find_one()
                self.connected = True
                print(f"✅ MongoDB conectado e autenticado: {self.db_name}")
                return True
            except Exception as auth_error:
                if "authentication" in str(auth_error).lower() or "unauthorized" in str(auth_error).lower():
                    print(f"⚠️  MongoDB conectado mas requer autenticação. Usando fallback JSON.")
                    print(f"   Para resolver: configure autenticação ou inicie MongoDB com --noauth")
                else:
                    print(f"⚠️  MongoDB conectado mas com erro de permissão: {auth_error}")
                self.connected = False
                return False
            
        except ConnectionFailure as e:
            print(f"🔌 MongoDB não encontrado. Usando fallback JSON.")
            self.connected = False
            return False
        except Exception as e:
            print(f"⚠️  Erro ao conectar MongoDB: {e}")
            print(f"🔄 Sistema funcionará com fallback JSON.")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Fecha a conexão com o MongoDB
        """
        if self.client:
            self.client.close()
            self.connected = False
            print("🔌 Desconectado do MongoDB")
    
    def is_connected(self) -> bool:
        """
        Verifica se está conectado ao MongoDB
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        if not self.connected or not self.client:
            return False
        
        try:
            # Testar conexão com ping
            self.client.admin.command('ping')
            return True
        except:
            self.connected = False
            return False
    
    def get_collection(self, collection_name: str):
        """
        Retorna uma coleção do MongoDB
        
        Args:
            collection_name: Nome da coleção
            
        Returns:
            Collection object ou None se não conectado
        """
        if not self.is_connected():
            if not self.connect():
                return None
        
        return self.db[collection_name]
    
    def create_index(self, collection_name: str, index_fields: List[tuple]):
        """
        Cria índices na coleção especificada
        
        Args:
            collection_name: Nome da coleção
            index_fields: Lista de tuplas (campo, direção) para criar índices
        """
        if not self.is_connected():
            return False
        
        try:
            collection = self.get_collection(collection_name)
            if collection is not None:
                existing_indexes = collection.index_information()
                
                for field, direction in index_fields:
                    index_name = f"{field}_1" if direction == 1 else f"{field}_-1"
                    
                    # Verificar se o índice já existe
                    if index_name not in existing_indexes:
                        collection.create_index([(field, direction)])
                        print(f"✅ Índice criado: {index_name} em {collection_name}")
                    else:
                        print(f"📋 Índice já existe: {index_name} em {collection_name}")
                
                return True
        except Exception as e:
            # Não mostrar erros de índices duplicados como críticos
            if "IndexKeySpecsConflict" not in str(e):
                print(f"❌ Erro ao criar índices: {e}")
            return False
    
    def fallback_to_json(self, operation: str, data: Any = None, file_path: str = "data/mongodb_fallback.json") -> Any:
        """
        Sistema de fallback para usar arquivo JSON quando MongoDB não está disponível
        
        Args:
            operation: 'read' ou 'write'
            data: Dados para escrever (apenas para operação 'write')
            file_path: Caminho do arquivo JSON de fallback
            
        Returns:
            Dados lidos (para 'read') ou sucesso da operação (para 'write')
        """
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if operation == 'read':
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return {}
            
            elif operation == 'write':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                return True
                
        except Exception as e:
            print(f"❌ Erro no fallback JSON: {e}")
            return {} if operation == 'read' else False


class NewsDatabase:
    """
    Gerenciador específico para dados de notícias no MongoDB
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializa o gerenciador de notícias
        
        Args:
            db_manager: Instância do DatabaseManager
        """
        self.db_manager = db_manager
        self.collection_name = "news_articles"
        self.metadata_collection = "news_metadata"
        self.details_collection = "article_details"
        
        # Criar índices se conectado
        if self.db_manager.is_connected():
            self._create_indexes()
    
    def _create_indexes(self):
        """
        Cria índices otimizados para consultas de notícias
        """
        if not self.db_manager.is_connected():
            return
            
        # Índices para artigos
        self.db_manager.create_index(self.collection_name, [
            ("link", 1),  # Índice único por link
            ("origem", 1),  # Filtrar por origem
            ("data_scraping", -1),  # Ordenar por data de scraping
            ("titulo", 1)  # Busca por título
        ])
        
        # Índices para metadados
        self.db_manager.create_index(self.metadata_collection, [
            ("origem", 1),
            ("ultimo_update", -1)
        ])
        
        # Índices para detalhes de artigos
        self.db_manager.create_index(self.details_collection, [
            ("link", 1),  # Índice único por link
            ("data_scraping", -1),  # Ordenar por data de scraping
            ("ultimo_acesso", -1)  # Rastrear último acesso
        ])
    
    def should_update_news(self, origem: str, hours_threshold: int = None) -> bool:
        """
        Verifica se deve atualizar notícias baseado no tempo desde a última atualização
        
        Args:
            origem: Nome da origem das notícias (ex: "TabNews")
            hours_threshold: Número de horas para considerar necessário atualizar (usa Config se None)
            
        Returns:
            bool: True se deve atualizar, False caso contrário
        """
        if hours_threshold is None:
            hours_threshold = Config.NEWS_UPDATE_INTERVAL_HOURS
            
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON para verificação
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/news_cache.json")
                if origem in fallback_data:
                    last_update_str = fallback_data[origem].get('timestamp')
                    if last_update_str:
                        last_update = datetime.fromisoformat(last_update_str)
                        threshold_time = datetime.now() - timedelta(hours=hours_threshold)
                        return last_update < threshold_time
                return True  # Se não há dados, deve atualizar
            
            collection = self.db_manager.get_collection(self.metadata_collection)
            metadata = collection.find_one({"origem": origem})
            
            if not metadata:
                return True  # Primeira vez, deve atualizar
            
            last_update = metadata.get('ultimo_update')
            if not last_update:
                return True
            
            # Verificar se passou o tempo mínimo
            threshold_time = datetime.now() - timedelta(hours=hours_threshold)
            should_update = last_update < threshold_time
            
            if should_update:
                print(f"⏰ Última atualização de {origem}: {last_update.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"⏰ Mais de {hours_threshold}h desde a última atualização. Atualizando...")
            else:
                time_diff = datetime.now() - last_update
                hours_left = hours_threshold - (time_diff.total_seconds() / 3600)
                print(f"⏳ {origem} atualizado recentemente. Próxima atualização em {hours_left:.1f}h")
            
            return should_update
            
        except Exception as e:
            # Não mostrar erros de autenticação repetidamente
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao verificar necessidade de atualização: {e}")
            return True  # Em caso de erro, melhor atualizar
    
    def save_articles(self, origem: str, articles: List[Dict]) -> bool:
        """
        Salva artigos no MongoDB
        
        Args:
            origem: Nome da origem (ex: "TabNews")
            articles: Lista de artigos para salvar
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/news_cache.json")
                fallback_data[origem] = {
                    "timestamp": datetime.now().isoformat(),
                    "articles": articles
                }
                return self.db_manager.fallback_to_json('write', fallback_data, file_path="data/news_cache.json")
            
            articles_collection = self.db_manager.get_collection(self.collection_name)
            metadata_collection = self.db_manager.get_collection(self.metadata_collection)
            
            # Remover artigos antigos desta origem
            articles_collection.delete_many({"origem": origem})
            
            # Adicionar timestamp de scraping aos artigos
            now = datetime.now()
            for article in articles:
                article['data_scraping'] = now
                article['origem'] = origem
            
            # Inserir novos artigos
            if articles:
                result = articles_collection.insert_many(articles)
                print(f"✅ {len(result.inserted_ids)} artigos salvos no MongoDB")
            
            # Atualizar metadados de última atualização
            metadata_collection.update_one(
                {"origem": origem},
                {
                    "$set": {
                        "ultimo_update": now,
                        "total_articles": len(articles)
                    }
                },
                upsert=True
            )
            
            return True
            
        except Exception as e:
            # Não mostrar erros de autenticação repetidamente
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao salvar artigos: {e}")
            return False
    
    def get_articles(self, origem: str, limit: int = 50) -> List[Dict]:
        """
        Recupera artigos do MongoDB
        
        Args:
            origem: Nome da origem
            limit: Número máximo de artigos para retornar
            
        Returns:
            Lista de artigos
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/news_cache.json")
                if origem in fallback_data:
                    return fallback_data[origem].get('articles', [])[:limit]
                return []
            
            collection = self.db_manager.get_collection(self.collection_name)
            
            # Buscar artigos ordenados por data de scraping (mais recentes primeiro)
            cursor = collection.find(
                {"origem": origem}
            ).sort("data_scraping", -1).limit(limit)
            
            articles = list(cursor)
            
            # Remover campos internos do MongoDB
            for article in articles:
                article.pop('_id', None)
                article.pop('data_scraping', None)
            
            return articles
            
        except Exception as e:
            # Não mostrar erros de autenticação repetidamente
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao recuperar artigos: {e}")
            return []
    
    def get_all_sources_stats(self) -> Dict[str, Dict]:
        """
        Retorna estatísticas de todas as fontes de notícias
        
        Returns:
            Dicionário com estatísticas por fonte
        """
        try:
            if not self.db_manager.is_connected():
                return {}
            
            metadata_collection = self.db_manager.get_collection(self.metadata_collection)
            stats = {}
            
            for metadata in metadata_collection.find():
                origem = metadata.get('origem')
                stats[origem] = {
                    'ultimo_update': metadata.get('ultimo_update'),
                    'total_articles': metadata.get('total_articles', 0)
                }
            
            return stats
            
        except Exception as e:
            # Não mostrar erros de autenticação repetidamente
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def should_update_article_details(self, link: str, hours_threshold: int = 6) -> bool:
        """
        Verifica se deve atualizar detalhes do artigo baseado no tempo desde a última atualização
        
        Args:
            link: URL do artigo
            hours_threshold: Número de horas para considerar necessário atualizar
            
        Returns:
            bool: True se deve atualizar, False caso contrário
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON para verificação
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/article_details_cache.json")
                if link in fallback_data:
                    last_update_str = fallback_data[link].get('ultimo_acesso')
                    if last_update_str:
                        last_update = datetime.fromisoformat(last_update_str)
                        threshold_time = datetime.now() - timedelta(hours=hours_threshold)
                        return last_update < threshold_time
                return True  # Se não há dados, deve atualizar
            
            collection = self.db_manager.get_collection(self.details_collection)
            article_details = collection.find_one({"link": link})
            
            if not article_details:
                return True  # Primeira vez, deve atualizar
            
            last_access = article_details.get('ultimo_acesso')
            if not last_access:
                return True
            
            # Verificar se passou o tempo mínimo
            threshold_time = datetime.now() - timedelta(hours=hours_threshold)
            should_update = last_access < threshold_time
            
            if should_update:
                print(f"⏰ Artigo acessado há mais de {hours_threshold}h. Atualizando...")
            else:
                time_diff = datetime.now() - last_access
                hours_left = hours_threshold - (time_diff.total_seconds() / 3600)
                print(f"⏳ Artigo em cache. Próxima atualização em {hours_left:.1f}h")
            
            return should_update
            
        except Exception as e:
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao verificar necessidade de atualização do artigo: {e}")
            return True  # Em caso de erro, melhor atualizar
    
    def save_article_details(self, link: str, titulo: str, conteudo: str, comentarios: List[Dict]) -> bool:
        """
        Salva detalhes completos do artigo no MongoDB
        
        Args:
            link: URL do artigo
            titulo: Título do artigo
            conteudo: Conteúdo completo do artigo
            comentarios: Lista de comentários
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/article_details_cache.json")
                fallback_data[link] = {
                    "titulo": titulo,
                    "conteudo": conteudo,
                    "comentarios": comentarios,
                    "ultimo_acesso": datetime.now().isoformat(),
                    "data_scraping": datetime.now().isoformat()
                }
                return self.db_manager.fallback_to_json('write', fallback_data, file_path="data/article_details_cache.json")
            
            collection = self.db_manager.get_collection(self.details_collection)
            
            now = datetime.now()
            article_data = {
                "link": link,
                "titulo": titulo,
                "conteudo": conteudo,
                "comentarios": comentarios,
                "ultimo_acesso": now,
                "data_scraping": now
            }
            
            # Usar upsert para atualizar se já existe
            result = collection.update_one(
                {"link": link},
                {"$set": article_data},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                print(f"✅ Detalhes do artigo salvos no MongoDB")
                return True
            else:
                print(f"⚠️  Nenhuma alteração feita nos detalhes do artigo")
                return True
            
        except Exception as e:
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao salvar detalhes do artigo: {e}")
            return False
    
    def get_article_details(self, link: str) -> Optional[Dict]:
        """
        Recupera detalhes completos do artigo do MongoDB
        
        Args:
            link: URL do artigo
            
        Returns:
            Dicionário com detalhes do artigo ou None se não encontrado
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/article_details_cache.json")
                return fallback_data.get(link)
            
            collection = self.db_manager.get_collection(self.details_collection)
            
            article_details = collection.find_one({"link": link})
            
            if article_details:
                # Remover campos internos do MongoDB
                article_details.pop('_id', None)
                return article_details
            
            return None
            
        except Exception as e:
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao recuperar detalhes do artigo: {e}")
            return None
    
    def cleanup_old_articles(self, days_threshold: int = 5) -> int:
        """
        Remove manualmente artigos mais antigos que o threshold (TTL automático deve cuidar disso)
        
        Args:
            days_threshold: Número de dias para considerar artigo antigo
            
        Returns:
            Número de artigos removidos
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON para limpeza manual
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/article_details_cache.json")
                removed_count = 0
                threshold_date = datetime.now() - timedelta(days=days_threshold)
                
                keys_to_remove = []
                for link, details in fallback_data.items():
                    data_scraping_str = details.get('data_scraping')
                    if data_scraping_str:
                        data_scraping = datetime.fromisoformat(data_scraping_str)
                        if data_scraping < threshold_date:
                            keys_to_remove.append(link)
                
                for key in keys_to_remove:
                    del fallback_data[key]
                    removed_count += 1
                
                if removed_count > 0:
                    self.db_manager.fallback_to_json('write', fallback_data, file_path="data/article_details_cache.json")
                    print(f"🧹 {removed_count} artigos antigos removidos do cache JSON")
                
                return removed_count
            
            collection = self.db_manager.get_collection(self.details_collection)
            
            # Calcular data limite
            threshold_date = datetime.now() - timedelta(days=days_threshold)
            
            # Remover artigos antigos
            result = collection.delete_many({
                "data_scraping": {"$lt": threshold_date}
            })
            
            if result.deleted_count > 0:
                print(f"🧹 {result.deleted_count} artigos antigos removidos do MongoDB")
            
            return result.deleted_count
            
        except Exception as e:
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao limpar artigos antigos: {e}")
            return 0
    
    def get_article_details_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas da coleção de detalhes de artigos
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            if not self.db_manager.is_connected():
                # Usar fallback JSON para estatísticas
                fallback_data = self.db_manager.fallback_to_json('read', file_path="data/article_details_cache.json")
                return {
                    'total_articles': len(fallback_data),
                    'source': 'JSON fallback'
                }
            
            collection = self.db_manager.get_collection(self.details_collection)
            
            total_count = collection.count_documents({})
            
            # Contar artigos dos últimos 7 dias
            week_ago = datetime.now() - timedelta(days=7)
            recent_count = collection.count_documents({
                "data_scraping": {"$gte": week_ago}
            })
            
            return {
                'total_articles': total_count,
                'recent_articles': recent_count,
                'source': 'MongoDB'
            }
            
        except Exception as e:
            if "authentication" not in str(e).lower() and "unauthorized" not in str(e).lower():
                print(f"❌ Erro ao obter estatísticas de detalhes: {e}")
            return {'total_articles': 0, 'recent_articles': 0, 'source': 'error'}