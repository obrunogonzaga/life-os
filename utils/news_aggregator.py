from typing import List, Dict
import json
import os
from datetime import datetime, timedelta
from scrapers.tabnews_scraper import TabNewsScraper, Artigo
from utils.database_manager import DatabaseManager, NewsDatabase


class NewsAggregator:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.scrapers = {
            "TabNews": TabNewsScraper()
            # Adicionar mais scrapers aqui conforme forem criados
        }
        
        # Inicializar MongoDB (com fallback para JSON se não conectar)
        self.db_manager = DatabaseManager()
        self.news_db = NewsDatabase(self.db_manager)
        
        # Manter cache em memória para compatibilidade
        self.cache_file = "data/news_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carrega cache de notícias"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Salva cache de notícias"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _is_cache_valid(self, site_name: str) -> bool:
        """Verifica se o cache ainda é válido (usando controle de 6 horas)"""
        # Usar MongoDB primeiro, fallback para JSON se não conectado
        return not self.news_db.should_update_news(site_name, hours_threshold=6)
    
    def _articles_to_dict(self, articles: List[Artigo]) -> List[Dict]:
        """Converte lista de Artigos para dicionários"""
        return [
            {
                "titulo": a.titulo,
                "link": a.link,
                "comentarios": a.comentarios,
                "autor": a.autor,
                "tempo_postagem": a.tempo_postagem,
                "origem": a.origem,
                "tags": a.tags
            }
            for a in articles
        ]
    
    def _dict_to_articles(self, data: List[Dict]) -> List[Artigo]:
        """Converte dicionários para lista de Artigos"""
        return [
            Artigo(
                titulo=d["titulo"],
                link=d["link"],
                comentarios=d["comentarios"],
                autor=d["autor"],
                tempo_postagem=d["tempo_postagem"],
                origem=d["origem"],
                tags=d.get("tags")
            )
            for d in data
        ]
    
    def get_news_from_site(self, site_name: str, force_update: bool = False) -> List[Artigo]:
        """Obtém notícias de um site específico"""
        if site_name not in self.scrapers:
            return []
        
        # Verificar se precisa atualizar (usa configuração do sistema)
        should_update = force_update or self.news_db.should_update_news(site_name)
        
        if not should_update:
            # Retornar dados do MongoDB/cache
            cached_articles = self.news_db.get_articles(site_name, limit=self.config_manager.get_max_articles())
            if cached_articles:
                return self._dict_to_articles(cached_articles)
        
        # Buscar novas notícias
        try:
            print(f"🔄 Atualizando notícias de {site_name}...")
            articles = self.scrapers[site_name].scrape_artigos()
            
            # Limitar número de artigos
            max_articles = self.config_manager.get_max_articles()
            articles = articles[:max_articles]
            
            # Salvar no MongoDB (com fallback para JSON)
            articles_dict = self._articles_to_dict(articles)
            self.news_db.save_articles(site_name, articles_dict)
            
            # Atualizar cache em memória para compatibilidade (sem campos de MongoDB)
            clean_articles = []
            for article in articles_dict:
                clean_article = article.copy()
                clean_article.pop('data_scraping', None)  # Remover campo datetime
                clean_articles.append(clean_article)
            
            self.cache[site_name] = {
                "timestamp": datetime.now().isoformat(),
                "articles": clean_articles
            }
            self._save_cache()
            
            print(f"✅ {len(articles)} notícias de {site_name} atualizadas")
            return articles
            
        except Exception as e:
            print(f"❌ Erro ao buscar notícias de {site_name}: {e}")
            
            # Tentar retornar dados salvos anteriormente
            cached_articles = self.news_db.get_articles(site_name, limit=self.config_manager.get_max_articles())
            if cached_articles:
                print(f"📦 Usando cache anterior de {site_name}")
                return self._dict_to_articles(cached_articles)
            
            # Fallback final para cache JSON
            if site_name in self.cache:
                print(f"📁 Usando fallback JSON para {site_name}")
                return self._dict_to_articles(self.cache[site_name]["articles"])
            
            return []
    
    def get_all_news(self, force_update: bool = False) -> List[Artigo]:
        """Obtém notícias de todos os sites ativos"""
        all_articles = []
        active_sites = self.config_manager.get_active_sites()
        
        for site in active_sites:
            articles = self.get_news_from_site(site, force_update)
            all_articles.extend(articles)
        
        # Opcional: ordenar por algum critério (implementar lógica de ordenação depois)
        return all_articles
    
    def get_database_stats(self) -> Dict:
        """
        Retorna estatísticas do banco de dados
        """
        stats = {
            "mongodb_connected": self.db_manager.is_connected(),
            "sources": self.news_db.get_all_sources_stats()
        }
        return stats
    
    def force_update_all(self) -> bool:
        """
        Força atualização de todas as fontes ativas
        """
        active_sites = self.config_manager.get_active_sites()
        success_count = 0
        
        for site in active_sites:
            try:
                articles = self.get_news_from_site(site, force_update=True)
                if articles:
                    success_count += 1
                    print(f"✅ {site}: {len(articles)} artigos atualizados")
                else:
                    print(f"⚠️  {site}: Nenhum artigo encontrado")
            except Exception as e:
                print(f"❌ {site}: Erro na atualização - {e}")
        
        print(f"\n📊 Atualização concluída: {success_count}/{len(active_sites)} fontes atualizadas")
        return success_count == len(active_sites)