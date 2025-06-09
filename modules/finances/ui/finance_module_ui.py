"""
Finance Module UI Orchestrator

This module provides the main UI orchestrator for the finance module,
integrating all UI components with the service layer and providing
a unified interface that maintains 100% compatibility with the original.
"""

from .base_ui import BaseUI
from .main_menu_ui import MainMenuUI
from .account_ui import AccountUI
from .card_ui import CardUI
from .transaction_ui import TransactionUI
from .alzi_ui import AlziUI
from .dashboard_ui import DashboardUI
from .import_ui import ImportUI

from ..services.finance_service import FinanceService
from utils.database_manager import DatabaseManager


class FinanceModuleUI(BaseUI):
    """Main UI orchestrator for the finance module"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database and services
        self.db_manager = DatabaseManager()
        self.finance_service = FinanceService(self.db_manager)
        
        # Initialize UI components
        self.main_menu_ui = MainMenuUI()
        self.account_ui = AccountUI(self.finance_service.account_service)
        self.card_ui = CardUI(self.finance_service.card_service, self.finance_service.account_service)
        self.transaction_ui = TransactionUI(
            self.finance_service.transaction_service,
            self.finance_service.account_service,
            self.finance_service.card_service
        )
        self.alzi_ui = AlziUI(self.finance_service.alzi_service)
        self.dashboard_ui = DashboardUI(self.finance_service)
        self.import_ui = ImportUI()
        
        # Build action handlers for main menu
        self.action_handlers = {
            "1": self.dashboard_ui.show_dashboard,
            "2": self.account_ui.show_menu,
            "3": self.card_ui.show_menu,
            "4": self.transaction_ui.show_menu,
            "5": self.alzi_ui.show_menu,
            "6": self.show_reports,
            "7": self.show_settings,
            "8": self.import_ui.show_menu,
            "9": self.dashboard_ui.show_statistics
        }
    
    def run(self):
        """
        Main entry point for the finance module
        Maintains 100% compatibility with the original interface
        """
        try:
            # Run the main menu loop with integrated services
            self.main_menu_ui.run_main_loop(self.action_handlers)
            
        except Exception as e:
            self.handle_exception(e, "módulo de finanças")
            self.show_error("Erro crítico no módulo de finanças")
    
    def show_reports(self):
        """Show reports and analysis (placeholder)"""
        self.clear()
        header = self.create_header_panel("📈 Relatórios e Análises")
        self.print(header)
        
        # Show reports submenu
        options = [
            ("1", "📊 Relatório Mensal"),
            ("2", "📈 Análise de Tendências"),
            ("3", "💳 Relatório de Cartões"),
            ("4", "🏦 Relatório de Contas"),
            ("5", "👫 Relatório Alzi Detalhado"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
        
        action_handlers = {
            "1": self._monthly_report,
            "2": self._trend_analysis,
            "3": self._cards_report,
            "4": self._accounts_report,
            "5": self._detailed_alzi_report
        }
        
        self.main_menu_ui.run_submenu_loop(
            "📈 Relatórios e Análises",
            options,
            action_handlers
        )
    
    def show_settings(self):
        """Show configuration settings (placeholder)"""
        self.clear()
        header = self.create_header_panel("⚙️ Configurações")
        self.print(header)
        
        # Show settings submenu
        options = [
            ("1", "🎨 Preferências de Interface"),
            ("2", "💱 Configurações de Moeda"),
            ("3", "📊 Configurações de Relatórios"),
            ("4", "🔄 Sincronização de Dados"),
            ("5", "🗄️ Configurações de Backup"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
        
        action_handlers = {
            "1": self._interface_settings,
            "2": self._currency_settings,
            "3": self._reports_settings,
            "4": self._sync_settings,
            "5": self._backup_settings
        }
        
        self.main_menu_ui.run_submenu_loop(
            "⚙️ Configurações",
            options,
            action_handlers
        )
    
    # ===============================
    # REPORT HANDLERS (PLACEHOLDERS)
    # ===============================
    
    def _monthly_report(self):
        """Monthly report (placeholder)"""
        self.clear()
        header = self.create_header_panel("📊 Relatório Mensal")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.show_info("Aqui será exibido:")
        self.print("• Resumo financeiro do mês")
        self.print("• Comparação com mês anterior")
        self.print("• Gráfico de gastos por categoria")
        self.print("• Análise de metas e orçamento")
        
        self.wait_for_enter()
    
    def _trend_analysis(self):
        """Trend analysis (placeholder)"""
        self.clear()
        header = self.create_header_panel("📈 Análise de Tendências")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _cards_report(self):
        """Cards report (placeholder)"""
        self.clear()
        header = self.create_header_panel("💳 Relatório de Cartões")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _accounts_report(self):
        """Accounts report (placeholder)"""
        self.clear()
        header = self.create_header_panel("🏦 Relatório de Contas")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _detailed_alzi_report(self):
        """Detailed Alzi report (placeholder)"""
        self.clear()
        header = self.create_header_panel("👫 Relatório Alzi Detalhado")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    # ===============================
    # SETTINGS HANDLERS (PLACEHOLDERS)
    # ===============================
    
    def _interface_settings(self):
        """Interface settings (placeholder)"""
        self.clear()
        header = self.create_header_panel("🎨 Preferências de Interface")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _currency_settings(self):
        """Currency settings (placeholder)"""
        self.clear()
        header = self.create_header_panel("💱 Configurações de Moeda")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _reports_settings(self):
        """Reports settings (placeholder)"""
        self.clear()
        header = self.create_header_panel("📊 Configurações de Relatórios")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _sync_settings(self):
        """Sync settings (placeholder)"""
        self.clear()
        header = self.create_header_panel("🔄 Sincronização de Dados")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def _backup_settings(self):
        """Backup settings (placeholder)"""
        self.clear()
        header = self.create_header_panel("🗄️ Configurações de Backup")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    # ===============================
    # UTILITY METHODS
    # ===============================
    
    def get_service_status(self) -> dict:
        """Get status of all services for debugging"""
        return {
            "database_connected": self.db_manager.is_connected(),
            "finance_service": self.finance_service is not None,
            "account_service": self.finance_service.account_service is not None,
            "card_service": self.finance_service.card_service is not None,
            "transaction_service": self.finance_service.transaction_service is not None,
            "alzi_service": self.finance_service.alzi_service is not None,
            "period_service": self.finance_service.period_service is not None
        }
    
    def health_check(self):
        """Perform a health check of all components"""
        self.clear()
        header = self.create_header_panel("🏥 Health Check do Sistema")
        self.print(header)
        
        status = self.get_service_status()
        
        self.print_newline()
        for component, is_healthy in status.items():
            icon = "✅" if is_healthy else "❌"
            self.print(f"{icon} {component.replace('_', ' ').title()}")
        
        self.print_newline()
        all_healthy = all(status.values())
        if all_healthy:
            self.show_success("Todos os componentes estão funcionando corretamente!")
        else:
            self.show_warning("Alguns componentes apresentam problemas")
        
        self.wait_for_enter()