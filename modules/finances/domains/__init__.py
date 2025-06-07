"""
Camada de Domínio do Módulo Finances

Esta camada contém as regras de negócio puras, sem dependências 
de infraestrutura, interface ou persistência.

Responsabilidades:
- Validações de dados
- Cálculos de negócio  
- Regras de domínio
- Lógica de transformação
"""

# Importações das classes de domínio - Fase 1 Completa
from .account_domain import AccountDomain
from .card_domain import CardDomain
from .transaction_domain import TransactionDomain
from .alzi_domain import AlziDomain
from .period_domain import PeriodDomain

__all__ = [
    'AccountDomain',
    'CardDomain',
    'TransactionDomain',
    'AlziDomain',
    'PeriodDomain'
]