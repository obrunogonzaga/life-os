#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Importar módulos do Life OS
from modules.news import WidiaNews
from modules.tools import ToolsModule
from modules.tasks import TasksModule
from modules.encora import EncoraModule
from modules.finances import FinancesModule
from utils.base_ui import BaseUI


class LifeOS(BaseUI):
    def __init__(self):
        super().__init__()
        self.running = True
        self.menu_options = [
            ("1", "📰 Notícias", "Últimas notícias de tecnologia"),
            ("2", "🔧 Ferramentas", "Utilitários e gerenciamento"),
            ("3", "📅 Agenda", "[dim italic]Em breve[/dim italic]"),
            ("4", "✅ Tarefas", "Gerenciamento com Todoist"),
            ("5", "🏢 Encora", "Ferramentas do trabalho"),
            ("6", "💰 Finanças", "Gestão financeira pessoal"),
            ("7", "📝 Notas", "[dim italic]Em breve[/dim italic]"),
            ("8", "🎯 Hábitos", "[dim italic]Em breve[/dim italic]"),
            ("0", "❌ Sair", "Encerrar o sistema")
        ]
    
    def show_header(self):
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        header_content = (
            f"[bold cyan]🧠 LIFE OS[/bold cyan]\n"
            f"[dim]Sistema de Organização Pessoal[/dim]\n"
            f"[dim]{current_date} • {current_time}[/dim]"
        )
        
        header_panel = self.create_panel(header_content, style="bright_blue")
        self.print(header_panel)
        self.print_newline()
    
    def show_menu(self):
        columns = [
            ("Opção", "cyan", 12),
            ("Módulo", "white", None),
            ("Descrição", "dim", None)
        ]
        
        data = []
        for option, module, description in self.menu_options:
            data.append([option, module, description])
        
        menu_table = self.create_data_table(columns, data, "Menu Principal")
        self.print(menu_table)
        self.print_newline()
    
    def launch_news_module(self):
        """Lança o módulo de notícias"""
        news_app = WidiaNews()
        news_app.run()
    
    def launch_tools_module(self):
        """Lança o módulo de ferramentas"""
        tools_app = ToolsModule()
        tools_app.run()
    
    def launch_tasks_module(self):
        """Lança o módulo de tarefas"""
        tasks_app = TasksModule()
        tasks_app.run()
    
    def launch_encora_module(self):
        """Lança o módulo Encora"""
        encora_app = EncoraModule()
        encora_app.run()
    
    def launch_finances_module(self):
        """Lança o módulo de finanças"""
        finances_app = FinancesModule()
        finances_app.run()
    
    def coming_soon(self, module_name):
        """Exibe mensagem de módulo em desenvolvimento"""
        self.clear()
        self.show_header()
        
        content = (
            f"[bold yellow]🚧 Módulo {module_name} em Desenvolvimento[/bold yellow]\n\n"
            f"[dim]Este módulo estará disponível em breve![/dim]"
        )
        
        panel = self.create_panel(content, style="yellow")
        self.print(panel)
        
        self.wait_for_enter("Pressione Enter para voltar ao menu principal...")
    
    def run(self):
        """Run the main Life OS application with standardized navigation"""
        action_handlers = {
            "1": self.launch_news_module,
            "2": self.launch_tools_module,
            "3": lambda: self.coming_soon("Agenda"),
            "4": self.launch_tasks_module,
            "5": self.launch_encora_module,
            "6": self.launch_finances_module,
            "7": lambda: self.coming_soon("Notas"),
            "8": lambda: self.coming_soon("Hábitos"),
            "0": self.exit_system
        }
        
        # Create menu options for the standardized menu system
        menu_options = [(option, f"{module} - {desc}") for option, module, desc in self.menu_options]
        
        while self.running:
            try:
                self.clear()
                self.show_header()
                self.show_menu()
                
                # Get user choice without automatic navigation (main menu handles 0 differently)
                choices = [option[0] for option in self.menu_options]
                choice = self.get_menu_choice("Escolha um módulo", choices, default="1")
                
                # Handle the choice
                if choice in action_handlers:
                    action_handlers[choice]()
                else:
                    self.show_error(f"Opção '{choice}' não reconhecida")
                    self.wait_for_enter()
                    
            except KeyboardInterrupt:
                self.show_warning("Sistema interrompido pelo usuário")
                self.exit_system()
            except Exception as e:
                self.handle_exception(e, "sistema principal")
                self.wait_for_enter()
    
    def exit_system(self):
        """Exit the Life OS system"""
        self.running = False
        self.show_success("Até logo! Tenha um ótimo dia! 👋")


if __name__ == "__main__":
    try:
        app = LifeOS()
        app.run()
    except KeyboardInterrupt:
        app = LifeOS()  # Create instance for UI methods
        app.show_warning("Sistema interrompido pelo usuário")
        sys.exit(0)