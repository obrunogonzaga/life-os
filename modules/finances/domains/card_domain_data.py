"""
Card Domain Data Layer - Camada de dados para cartões

Implementação mínima para permitir funcionamento dos services.
"""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from utils.database_manager import DatabaseManager
from utils.finance_models import CartaoCredito, BandeiraCartao


class CardDomainData:
    """Implementa operações de dados para cartões"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = "cartoes_credito"
        self.fallback_file = Path("data/finance_cards.json")
        self.fallback_file.parent.mkdir(exist_ok=True)
    
    def create_card(self, nome: str, banco: str, bandeira: BandeiraCartao, 
                   limite: float, dia_vencimento: int, dia_fechamento: int,
                   conta_vinculada_id: Optional[str] = None,
                   compartilhado_com_alzi: bool = False) -> Optional[CartaoCredito]:
        """Cria um novo cartão de crédito"""
        try:
            card_data = {
                'id': str(uuid.uuid4()),
                'nome': nome,
                'banco': banco,
                'bandeira': bandeira,
                'limite': limite,
                'limite_disponivel': limite,
                'dia_vencimento': dia_vencimento,
                'dia_fechamento': dia_fechamento,
                'conta_vinculada_id': conta_vinculada_id,
                'compartilhado_com_alzi': compartilhado_com_alzi,
                'ativo': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if self.db_manager.is_connected():
                self.db_manager.collection(self.collection_name).insert_one(card_data)
            
            return CartaoCredito.from_dict(card_data)
        except Exception as e:
            print(f"Erro ao criar cartão: {e}")
            return None
    
    def get_card_by_id(self, card_id: str) -> Optional[CartaoCredito]:
        """Obtém um cartão pelo ID"""
        try:
            if self.db_manager.is_connected():
                doc = self.db_manager.collection(self.collection_name).find_one({"id": card_id})
                if doc:
                    return CartaoCredito.from_dict(doc)
            else:
                # Fallback para arquivo JSON
                cards = self._load_from_fallback()
                for card_data in cards:
                    if card_data.get('id') == card_id:
                        return CartaoCredito.from_dict(card_data)
            
            return None
        except Exception as e:
            print(f"Erro ao buscar cartão por ID: {e}")
            return None
    
    def list_cards(self, active_only: bool = True) -> List[CartaoCredito]:
        """Lista cartões"""
        try:
            cards = []
            
            if self.db_manager.is_connected():
                # Buscar no MongoDB
                query = {"ativo": True} if active_only else {}
                docs = self.db_manager.collection(self.collection_name).find(query)
                for doc in docs:
                    try:
                        card = CartaoCredito.from_dict(doc)
                        cards.append(card)
                    except Exception as e:
                        print(f"Erro ao converter cartão: {e}")
                        continue
            else:
                # Fallback para arquivo JSON
                cards_data = self._load_from_fallback()
                for card_data in cards_data:
                    if not active_only or card_data.get('ativo', True):
                        try:
                            card = CartaoCredito.from_dict(card_data)
                            cards.append(card)
                        except Exception as e:
                            print(f"Erro ao converter cartão do fallback: {e}")
                            continue
            
            return cards
        except Exception as e:
            print(f"Erro ao listar cartões: {e}")
            return []
    
    def update_card(self, card_id: str, **kwargs) -> bool:
        """Atualiza um cartão"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            
            if self.db_manager.is_connected():
                # Atualizar no MongoDB
                result = self.db_manager.collection(self.collection_name).update_one(
                    {"id": card_id}, 
                    {"$set": kwargs}
                )
                return result.modified_count > 0
            else:
                # Fallback para arquivo JSON
                cards_data = self._load_from_fallback()
                for card_data in cards_data:
                    if card_data.get('id') == card_id:
                        card_data.update(kwargs)
                        self._save_to_fallback(cards_data)
                        return True
                return False
            
        except Exception as e:
            print(f"Erro ao atualizar cartão: {e}")
            return False

    def _load_from_fallback(self) -> List[Dict[str, Any]]:
        """Carrega cartões do arquivo JSON de fallback"""
        try:
            if self.fallback_file.exists():
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Erro ao carregar fallback: {e}")
            return []

    def _save_to_fallback(self, cards_data: List[Dict[str, Any]]):
        """Salva cartões no arquivo JSON de fallback"""
        try:
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(cards_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Erro ao salvar fallback: {e}")