"""
Main Menu UI for Finance Module

This module provides the main menu interface for the finance module,
handling navigation and orchestrating the different UI components.
"""

from typing import Dict, Callable
from .base_ui import BaseUI


class MainMenuUI(BaseUI):
    """Main menu interface for the finance module"""
    
    def __init__(self):
        super().__init__()
        self.menu_options = self._build_menu_options()
    
    def _build_menu_options(self) -> list:
        """Build the main menu options"""
        return [
            ("1", "📊 Dashboard Financeiro"),
            ("2", "🏦 Gerenciar Contas Correntes"),
            ("3", "💳 Gerenciar Cartões de Crédito"),
            ("4", "📝 Gerenciar Transações"),
            ("5", "👫 Transações Compartilhadas com Alzi"),
            ("6", "📈 Relatórios e Análises"),
            ("7", "⚙️ Configurações"),
            ("8", "📤 Importar/Exportar Dados"),
            ("9", "📊 Estatísticas Avançadas"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
    
    def show_main_menu(self):
        """Display the main finance menu"""
        self.clear()
        
        # Header
        header = self.create_header_panel(
            "💰 MÓDULO DE FINANÇAS", 
            "Gestão Financeira Pessoal"
        )
        self.print(header)
        
        # Menu options
        menu_table = self.create_menu_table(self.menu_options)
        self.print(menu_table)
        self.print_newline()
    
    def get_user_choice(self) -> str:
        """Get user menu choice"""
        choices = [option[0] for option in self.menu_options]
        return self.get_menu_choice("Escolha uma opção", choices)
    
    def run_main_loop(self, action_handlers: Dict[str, Callable]):
        """
        Run the main menu loop
        
        Args:
            action_handlers: Dictionary mapping menu options to handler functions
        """
        while True:
            try:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice.upper() == "M":
                    break
                
                # Execute the chosen action
                if choice in action_handlers:
                    action_handlers[choice]()
                else:
                    self.show_error(f"Opção '{choice}' não implementada")
                    self.wait_for_enter()
                    
            except KeyboardInterrupt:
                self.show_warning("Saindo do módulo de finanças...")
                break
            except Exception as e:
                self.handle_exception(e, "menu principal")
                self.wait_for_enter()
    
    def show_submenu(self, title: str, options: list) -> str:
        """
        Show a submenu and get user choice
        
        Args:
            title: Submenu title
            options: List of (option, description) tuples
            
        Returns:
            User's choice
        """
        self.clear()
        
        # Header
        header = self.create_header_panel(title)
        self.print(header)
        
        # Menu options
        menu_table = self.create_menu_table(options)
        self.print(menu_table)
        self.print_newline()
        
        # Get choice
        choices = [option[0] for option in options]
        return self.get_menu_choice("Escolha uma opção", choices)
    
    def run_submenu_loop(self, title: str, options: list, 
                        action_handlers: Dict[str, Callable]):
        """
        Run a submenu loop
        
        Args:
            title: Submenu title
            options: List of (option, description) tuples
            action_handlers: Dictionary mapping options to handler functions
        """
        while True:
            try:
                choice = self.show_submenu(title, options)
                
                if choice.upper() == "M":
                    break
                
                # Execute the chosen action
                if choice in action_handlers:
                    action_handlers[choice]()
                else:
                    self.show_error(f"Opção '{choice}' não implementada")
                    self.wait_for_enter()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.handle_exception(e, "submenu")
                self.wait_for_enter()