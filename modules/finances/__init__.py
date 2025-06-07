"""
Módulo Finances - Sistema de Gestão Financeira Pessoal

Este módulo fornece funcionalidades completas para gestão financeira pessoal,
incluindo contas correntes, cartões de crédito, transações e relatórios.

Arquitetura:
- domains/: Regras de negócio puras  
- services/: Operações de negócio
- ui/: Interfaces de usuário
"""

# Import da classe principal do arquivo finances.py
import sys
import importlib.util
from pathlib import Path

# Importar FinancesModule do arquivo finances.py
_finances_file = Path(__file__).parent.parent / 'finances.py'
_spec = importlib.util.spec_from_file_location('finances_module', _finances_file)
_finances_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_finances_module)

# Expor a classe FinancesModule
FinancesModule = _finances_module.FinancesModule

# Também expor os domains para uso futuro
from .domains import (
    AccountDomain,
    CardDomain, 
    TransactionDomain,
    AlziDomain,
    PeriodDomain
)

__all__ = [
    'FinancesModule',  # Classe principal do sistema
    'AccountDomain',
    'CardDomain',
    'TransactionDomain', 
    'AlziDomain',
    'PeriodDomain'
]