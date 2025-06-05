#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from datetime import datetime

# Importar módulos do Life OS
from modules.news import WidiaNews
from modules.tools import ToolsModule


console = Console()


class LifeOS:
    def __init__(self):
        self.running = True
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_header(self):
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        console.print(Panel.fit(
            f"[bold cyan]🧠 LIFE OS[/bold cyan]\n"
            f"[dim]Sistema de Organização Pessoal[/dim]\n"
            f"[dim]{current_date} • {current_time}[/dim]",
            border_style="bright_blue"
        ))
        console.print()
    
    def show_menu(self):
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("Opção", style="cyan", width=12)
        table.add_column("Módulo", style="white")
        table.add_column("Descrição", style="dim")
        
        table.add_row("1", "📰 Notícias", "Últimas notícias de tecnologia")
        table.add_row("2", "🔧 Ferramentas", "Utilitários e gerenciamento")
        table.add_row("3", "📅 Agenda", "[dim italic]Em breve[/dim italic]")
        table.add_row("4", "✅ Tarefas", "[dim italic]Em breve[/dim italic]")
        table.add_row("5", "💰 Finanças", "[dim italic]Em breve[/dim italic]")
        table.add_row("6", "📝 Notas", "[dim italic]Em breve[/dim italic]")
        table.add_row("7", "🎯 Hábitos", "[dim italic]Em breve[/dim italic]")
        table.add_row("0", "❌ Sair", "Encerrar o sistema")
        
        console.print(table)
        console.print()
    
    def launch_news_module(self):
        """Lança o módulo de notícias"""
        news_app = WidiaNews()
        news_app.run()
    
    def launch_tools_module(self):
        """Lança o módulo de ferramentas"""
        tools_app = ToolsModule()
        tools_app.run()
    
    def coming_soon(self, module_name):
        """Exibe mensagem de módulo em desenvolvimento"""
        self.clear_screen()
        self.show_header()
        
        console.print(Panel(
            f"[bold yellow]🚧 Módulo {module_name} em Desenvolvimento[/bold yellow]\n\n"
            f"[dim]Este módulo estará disponível em breve![/dim]",
            border_style="yellow",
            padding=(2, 4)
        ))
        
        console.print("\n[dim]Pressione Enter para voltar ao menu principal...[/dim]")
        input()
    
    def run(self):
        while self.running:
            self.clear_screen()
            self.show_header()
            self.show_menu()
            
            choice = Prompt.ask("Escolha um módulo", default="1")
            
            if choice == "1":
                self.launch_news_module()
            elif choice == "2":
                self.launch_tools_module()
            elif choice == "3":
                self.coming_soon("Agenda")
            elif choice == "4":
                self.coming_soon("Tarefas")
            elif choice == "5":
                self.coming_soon("Finanças")
            elif choice == "6":
                self.coming_soon("Notas")
            elif choice == "7":
                self.coming_soon("Hábitos")
            elif choice == "0":
                self.running = False
                console.print("\n[bold green]Até logo! Tenha um ótimo dia! 👋[/bold green]")
            else:
                console.print("\n[red]Opção inválida![/red]")
                console.print("[dim]Pressione Enter para continuar...[/dim]")
                input()


if __name__ == "__main__":
    try:
        app = LifeOS()
        app.run()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Sistema interrompido pelo usuário[/bold red]")
        sys.exit(0)