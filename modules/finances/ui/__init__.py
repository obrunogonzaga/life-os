"""
UI Layer for Finance Module

This package contains all user interface components for the finance module,
implementing the presentation layer of the Domain-Driven Design architecture.

Structure:
- base_ui.py: Common UI utilities and Rich components
- main_menu_ui.py: Main menu interface and navigation
- account_ui.py: Account management interface
- card_ui.py: Credit card management interface
- transaction_ui.py: Transaction management interface
- alzi_ui.py: Shared expenses interface
- dashboard_ui.py: Dashboard and analytics interface
- import_ui.py: Data import/export interface
- finance_module_ui.py: Main UI orchestrator
"""

from .base_ui import BaseUI
from .main_menu_ui import MainMenuUI
from .account_ui import AccountUI
from .card_ui import CardUI
from .transaction_ui import TransactionUI
from .alzi_ui import AlziUI
from .dashboard_ui import DashboardUI
from .import_ui import ImportUI
from .finance_module_ui import FinanceModuleUI

__all__ = [
    'BaseUI',
    'MainMenuUI', 
    'AccountUI',
    'CardUI',
    'TransactionUI',
    'AlziUI',
    'DashboardUI',
    'ImportUI',
    'FinanceModuleUI'
]