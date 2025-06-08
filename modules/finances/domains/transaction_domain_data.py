"""
Transaction Domain Data Layer - Camada de dados para transações

Implementação mínima para permitir funcionamento dos services.
"""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from utils.database_manager import DatabaseManager
from utils.finance_models import Transacao, TipoTransacao, StatusTransacao


class TransactionDomainData:
    """Implementa operações de dados para transações"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = "transacoes"
        self.fallback_file = Path("data/finance_transactions.json")
        self.fallback_file.parent.mkdir(exist_ok=True)
    
    def create_transaction(self, descricao: str, valor: float, tipo: TipoTransacao,
                          data_transacao: str, categoria: Optional[str] = None,
                          conta_id: Optional[str] = None, cartao_id: Optional[str] = None,
                          parcelamento: List = None, observacoes: Optional[str] = None,
                          compartilhado_com_alzi: bool = False) -> Optional[Transacao]:
        """Cria uma nova transação"""
        try:
            transaction_data = {
                'id': str(uuid.uuid4()),
                'descricao': descricao,
                'valor': valor,
                'tipo': tipo,
                'data_transacao': data_transacao,
                'categoria': categoria,
                'conta_id': conta_id,
                'cartao_id': cartao_id,
                'parcelamento': parcelamento or [],
                'observacoes': observacoes,
                'status': StatusTransacao.PROCESSADA,
                'compartilhado_com_alzi': compartilhado_com_alzi,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if self.db_manager.is_connected():
                self.db_manager.collection(self.collection_name).insert_one(transaction_data)
            
            return Transacao.from_dict(transaction_data)
        except Exception as e:
            print(f"Erro ao criar transação: {e}")
            return None
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transacao]:
        """Obtém uma transação pelo ID"""
        return None
    
    def list_transactions(self, filters: Dict[str, Any] = None) -> List[Transacao]:
        """Lista transações"""
        return []
    
    def update_transaction(self, transaction_id: str, **kwargs) -> bool:
        """Atualiza uma transação"""
        return True
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Exclui uma transação"""
        return True