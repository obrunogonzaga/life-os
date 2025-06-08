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
        # Implementação básica para testes
        return None
    
    def list_cards(self, active_only: bool = True) -> List[CartaoCredito]:
        """Lista cartões"""
        return []
    
    def update_card(self, card_id: str, **kwargs) -> bool:
        """Atualiza um cartão"""
        return True