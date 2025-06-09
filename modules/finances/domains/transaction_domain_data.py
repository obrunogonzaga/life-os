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
        try:
            if self.db_manager.is_connected():
                doc = self.db_manager.collection(self.collection_name).find_one({"id": transaction_id})
                if doc:
                    return self._document_to_transacao(doc)
            else:
                # Fallback para arquivo JSON
                transactions = self._load_from_fallback()
                for trans_data in transactions:
                    if trans_data.get('id') == transaction_id:
                        return Transacao.from_dict(trans_data)
            return None
        except Exception as e:
            print(f"Erro ao buscar transação: {e}")
            return None
    
    def list_transactions(self, filters: Dict[str, Any] = None) -> List[Transacao]:
        """Lista transações"""
        try:
            if filters is None:
                filters = {}
                
            if self.db_manager.is_connected():
                docs = list(self.db_manager.collection(self.collection_name).find(filters))
                
                transactions = []
                for doc in docs:
                    try:
                        trans = self._document_to_transacao(doc)
                        transactions.append(trans)
                    except Exception as conv_error:
                        print(f"Erro ao converter transação: {conv_error}")
                
                return transactions
            else:
                # Fallback para arquivo JSON
                transactions = self._load_from_fallback()
                result = [Transacao.from_dict(trans_data) for trans_data in transactions if self._matches_filters(trans_data, filters)]
                return result
        except Exception as e:
            print(f"Erro ao listar transações: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_transaction(self, transaction_id: str, **kwargs) -> bool:
        """Atualiza uma transação"""
        try:
            # Adicionar timestamp de atualização
            kwargs['updated_at'] = datetime.now().isoformat()
            
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.collection_name).update_one(
                    {"id": transaction_id}, 
                    {"$set": kwargs}
                )
                return result.modified_count > 0
            else:
                # Fallback para arquivo JSON
                transactions = self._load_from_fallback()
                for trans_data in transactions:
                    if trans_data.get('id') == transaction_id:
                        trans_data.update(kwargs)
                        self._save_to_fallback(transactions)
                        return True
                return False
        except Exception as e:
            print(f"Erro ao atualizar transação: {e}")
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Exclui uma transação"""
        try:
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.collection_name).delete_one({"id": transaction_id})
                return result.deleted_count > 0
            else:
                # Fallback para arquivo JSON
                transactions = self._load_from_fallback()
                original_count = len(transactions)
                transactions = [t for t in transactions if t.get('id') != transaction_id]
                if len(transactions) < original_count:
                    self._save_to_fallback(transactions)
                    return True
                return False
        except Exception as e:
            print(f"Erro ao excluir transação: {e}")
            return False
    
    def _document_to_transacao(self, doc: Dict[str, Any]) -> Transacao:
        """Converte documento do MongoDB para objeto Transacao"""
        # Remover _id do MongoDB se existir
        if '_id' in doc:
            del doc['_id']
        
        # Converter tipos enum se necessário
        if 'tipo' in doc and isinstance(doc['tipo'], str):
            doc['tipo'] = TipoTransacao(doc['tipo'])
        
        if 'status' in doc and isinstance(doc['status'], str):
            doc['status'] = StatusTransacao(doc['status'])
        
        return Transacao.from_dict(doc)
    
    def _load_from_fallback(self) -> List[Dict[str, Any]]:
        """Carrega transações do arquivo de fallback"""
        try:
            if self.fallback_file.exists():
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def _save_to_fallback(self, transactions: List[Dict[str, Any]]) -> None:
        """Salva transações no arquivo de fallback"""
        try:
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(transactions, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Erro ao salvar no fallback: {e}")
    
    def _matches_filters(self, trans_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Verifica se transação atende aos filtros"""
        for key, value in filters.items():
            if key not in trans_data or trans_data[key] != value:
                return False
        return True