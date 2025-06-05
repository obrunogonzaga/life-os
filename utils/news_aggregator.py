from typing import List, Dict
import json
import os
from datetime import datetime, timedelta
from scrapers.tabnews_scraper import TabNewsScraper, Artigo


class NewsAggregator:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.scrapers = {
            "TabNews": TabNewsScraper()
            # Adicionar mais scrapers aqui conforme forem criados
        }
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
        """Verifica se o cache ainda é válido"""
        if site_name not in self.cache:
            return False
        
        cached_time = datetime.fromisoformat(self.cache[site_name]["timestamp"])
        cache_duration = timedelta(seconds=self.config_manager.get_cache_duration())
        
        return datetime.now() - cached_time < cache_duration
    
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
        
        # Verificar cache
        if not force_update and self._is_cache_valid(site_name):
            return self._dict_to_articles(self.cache[site_name]["articles"])
        
        # Buscar novas notícias
        try:
            articles = self.scrapers[site_name].scrape_artigos()
            
            # Limitar número de artigos
            max_articles = self.config_manager.get_max_articles()
            articles = articles[:max_articles]
            
            # Atualizar cache
            self.cache[site_name] = {
                "timestamp": datetime.now().isoformat(),
                "articles": self._articles_to_dict(articles)
            }
            self._save_cache()
            
            return articles
        except Exception as e:
            print(f"Erro ao buscar notícias de {site_name}: {e}")
            # Retornar cache antigo se houver
            if site_name in self.cache:
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