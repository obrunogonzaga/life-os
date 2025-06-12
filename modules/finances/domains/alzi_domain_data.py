"""
Alzi Domain Data Layer - Camada de dados para compartilhamento com Alzi

Implementação mínima para permitir funcionamento dos services.
"""

from typing import List
from datetime import datetime

from utils.database_manager import DatabaseManager
from utils.finance_models import Transacao


class AlziDomainData:
    """Implementa operações de dados para gastos compartilhados com Alzi"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_shared_transactions_by_month(self, ano: int, mes: int) -> List[Transacao]:
        """Obtém transações compartilhadas de um mês específico"""
        from modules.finances.services.transaction_service import TransactionService
        from modules.finances.services.card_service import CardService
        from modules.finances.domains.transaction_domain import TransactionDomain
        
        # Create services
        transaction_service = TransactionService(self.db_manager)
        card_service = CardService(self.db_manager)
        
        all_transactions = transaction_service.list_transactions()
        
        # Filter transactions that are shared with Alzi and match the year/month
        shared_transactions = []
        for trans in all_transactions:
            # Check if transaction is shared with Alzi
            if hasattr(trans, 'compartilhado_com_alzi') and trans.compartilhado_com_alzi:
                try:
                    # For credit card transactions, use invoice period
                    if trans.cartao_id:
                        card = card_service.get_card_by_id(trans.cartao_id)
                        if card:
                            # Calculate which invoice this transaction belongs to
                            trans_date = datetime.strptime(trans.data_transacao[:10], "%Y-%m-%d").date()
                            invoice_month, invoice_year = TransactionDomain.calculate_invoice_month_for_transaction(
                                trans_date, card.dia_fechamento
                            )
                            if invoice_year == ano and invoice_month == mes:
                                shared_transactions.append(trans)
                    else:
                        # For debit/account transactions, use transaction date
                        trans_date = datetime.strptime(trans.data_transacao[:10], "%Y-%m-%d")
                        if trans_date.year == ano and trans_date.month == mes:
                            shared_transactions.append(trans)
                except (ValueError, AttributeError):
                    continue
        
        return shared_transactions
