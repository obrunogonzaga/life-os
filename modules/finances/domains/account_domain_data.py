"""
Account Domain Data Layer - Camada de dados para contas

Esta classe implementa as operações de dados para contas correntes,
separando a lógica de persistência das regras de negócio.
"""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from utils.database_manager import DatabaseManager
from utils.finance_models import ContaCorrente, TipoConta
from .account_domain import AccountDomain


class AccountDomainData:
    """
    Implementa operações de dados para contas usando DatabaseManager
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = "contas_correntes"
        self.fallback_file = Path("data/finance_accounts.json")
        self.fallback_file.parent.mkdir(exist_ok=True)
        
        # Ensure indexes exist
        self._create_indexes()
    
    def _create_indexes(self):
        """Cria índices para otimizar as consultas"""
        if self.db_manager.is_connected():
            try:
                collection = self.db_manager.collection(self.collection_name)
                collection.create_index("id", unique=True)
                collection.create_index("compartilhado_com_alzi")
                collection.create_index([("banco", 1), ("agencia", 1), ("conta", 1)])
            except Exception as e:
                print(f"Aviso: Não foi possível criar índices para contas: {e}")
    
    def _load_fallback_data(self) -> List[Dict]:
        """Carrega dados do arquivo JSON de fallback"""
        if self.fallback_file.exists():
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def _save_fallback_data(self, data: List[Dict]):
        """Salva dados no arquivo JSON de fallback"""
        try:
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados de fallback de contas: {e}")
    
    def create_account(self, nome: str, banco: str, agencia: str, conta: str, 
                      tipo: TipoConta, saldo_inicial: float, 
                      compartilhado_com_alzi: bool = False) -> Optional[ContaCorrente]:
        """Cria uma nova conta corrente"""
        try:
            # Preparar dados usando domain
            account_data = AccountDomain.prepare_account_creation_data(
                nome, banco, agencia, conta, tipo, saldo_inicial, compartilhado_com_alzi
            )
            
            # Salvar no banco
            if self.db_manager.is_connected():
                self.db_manager.collection(self.collection_name).insert_one(account_data)
            else:
                # Fallback para JSON
                data = self._load_fallback_data()
                data.append(account_data)
                self._save_fallback_data(data)
            
            # Retornar objeto ContaCorrente
            return ContaCorrente.from_dict(account_data)
            
        except Exception as e:
            print(f"Erro ao criar conta: {e}")
            return None
    
    def get_account_by_id(self, account_id: str) -> Optional[ContaCorrente]:
        """Obtém uma conta pelo ID"""
        try:
            if self.db_manager.is_connected():
                doc = self.db_manager.collection(self.collection_name).find_one({"id": account_id})
                if doc:
                    return ContaCorrente.from_dict(doc)
            else:
                data = self._load_fallback_data()
                for account_data in data:
                    if account_data["id"] == account_id:
                        return ContaCorrente.from_dict(account_data)
            
            return None
        except Exception as e:
            print(f"Erro ao obter conta: {e}")
            return None
    
    def list_accounts(self, active_only: bool = True) -> List[ContaCorrente]:
        """Lista todas as contas correntes"""
        try:
            if self.db_manager.is_connected():
                filtro = {"ativa": True} if active_only else {}
                docs = list(self.db_manager.collection(self.collection_name).find(filtro))
            else:
                data = self._load_fallback_data()
                docs = data
                if active_only:
                    docs = [d for d in docs if d.get("ativa", True)]
            
            return [ContaCorrente.from_dict(doc) for doc in docs]
        except Exception as e:
            print(f"Erro ao listar contas: {e}")
            return []
    
    def update_account(self, account_id: str, **kwargs) -> bool:
        """Atualiza uma conta corrente"""
        try:
            # Obter conta atual para validações
            current_account = self.get_account_by_id(account_id)
            if not current_account:
                return False
            
            # Preparar dados usando domain
            update_data = AccountDomain.prepare_account_update_data(current_account, **kwargs)
            
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.collection_name).update_one(
                    {"id": account_id}, {"$set": update_data}
                )
                return result.modified_count > 0
            else:
                data = self._load_fallback_data()
                for i, account_data in enumerate(data):
                    if account_data["id"] == account_id:
                        data[i].update(update_data)
                        self._save_fallback_data(data)
                        return True
                return False
        except Exception as e:
            print(f"Erro ao atualizar conta: {e}")
            return False
    
    def delete_account(self, account_id: str) -> bool:
        """Exclui uma conta corrente (hard delete - use com cuidado)"""
        try:
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.collection_name).delete_one({"id": account_id})
                return result.deleted_count > 0
            else:
                data = self._load_fallback_data()
                original_length = len(data)
                data[:] = [d for d in data if d["id"] != account_id]
                if len(data) < original_length:
                    self._save_fallback_data(data)
                    return True
                return False
        except Exception as e:
            print(f"Erro ao excluir conta: {e}")
            return False
    
    def account_exists(self, banco: str, agencia: str, conta: str, 
                      exclude_id: Optional[str] = None) -> bool:
        """Verifica se já existe uma conta com os mesmos dados"""
        try:
            accounts = self.list_accounts(active_only=False)
            
            for acc in accounts:
                if (acc.banco.lower() == banco.lower() and 
                    acc.agencia == agencia and 
                    acc.conta == conta and
                    acc.id != exclude_id):
                    return True
            
            return False
        except Exception:
            return False