"""
Alzi Domain Data Layer - Camada de dados para compartilhamento com Alzi

Implementação mínima para permitir funcionamento dos services.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from utils.database_manager import DatabaseManager
from utils.finance_models import Transacao


class AlziDomainData:
    """Implementa operações de dados para gastos compartilhados com Alzi"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_shared_transactions_by_month(self, ano: int, mes: int) -> List[Transacao]:
        """Obtém transações compartilhadas de um mês específico"""
        return []