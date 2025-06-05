import json
import os
from typing import List, Dict, Any


class ConfigManager:
    def __init__(self, config_file="data/config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo ou cria um novo"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Configuração padrão
            default_config = {
                "active_sites": ["TabNews"],
                "available_sites": ["TabNews"],  # Adicionar mais conforme criar scrapers
                "cache_duration": 300,  # 5 minutos
                "max_articles": 50
            }
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any] = None):
        """Salva configurações no arquivo"""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_active_sites(self) -> List[str]:
        """Retorna lista de sites ativos"""
        return self.config.get("active_sites", [])
    
    def get_available_sites(self) -> List[str]:
        """Retorna lista de sites disponíveis"""
        return self.config.get("available_sites", [])
    
    def add_site(self, site_name: str) -> bool:
        """Adiciona um site à lista de ativos"""
        if site_name in self.config["available_sites"]:
            if site_name not in self.config["active_sites"]:
                self.config["active_sites"].append(site_name)
                self._save_config()
            return True
        return False
    
    def remove_site(self, site_name: str) -> bool:
        """Remove um site da lista de ativos"""
        if site_name in self.config["active_sites"]:
            self.config["active_sites"].remove(site_name)
            self._save_config()
            return True
        return False
    
    def get_cache_duration(self) -> int:
        """Retorna duração do cache em segundos"""
        return self.config.get("cache_duration", 300)
    
    def get_max_articles(self) -> int:
        """Retorna número máximo de artigos por site"""
        return self.config.get("max_articles", 50)