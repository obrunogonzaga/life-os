#!/usr/bin/env python3
import os
import sys
from typing import List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box
from utils.config_manager import ConfigManager
from utils.news_aggregator import NewsAggregator
from scrapers.tabnews_scraper import Artigo


console = Console()


class WidiaNews:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.news_aggregator = NewsAggregator(self.config_manager)
        self.running = True
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_header(self):
        console.print(Panel.fit(
            "[bold cyan]🗞️  WIDIA NEWS[/bold cyan]\n"
            "[dim]Seu agregador de notícias tech[/dim]",
            border_style="bright_blue"
        ))
        console.print()
    
    def show_menu(self):
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("Opção", style="cyan", width=12)
        table.add_column("Descrição", style="white")
        
        table.add_row("1", "📰 Últimas notícias")
        table.add_row("2", "➕ Adicionar site")
        table.add_row("3", "➖ Remover site")
        table.add_row("4", "📋 Listar sites ativos")
        table.add_row("5", "🔄 Atualizar notícias")
        table.add_row("0", "❌ Sair")
        
        console.print(table)
        console.print()
    
    def show_latest_news(self):
        self.clear_screen()
        self.show_header()
        
        console.print("[bold yellow]📰 Carregando últimas notícias...[/bold yellow]\n")
        
        try:
            articles = self.news_aggregator.get_all_news()
            
            if not articles:
                console.print("[red]Nenhuma notícia encontrada![/red]")
                console.print("[dim]Verifique se há sites ativos ou tente atualizar.[/dim]")
            else:
                # Ordenar por mais recente (você pode implementar uma lógica melhor depois)
                console.print(f"[green]Encontradas {len(articles)} notícias[/green]\n")
                
                for i, article in enumerate(articles[:20], 1):  # Limitar a 20 notícias
                    # Criar um painel para cada notícia
                    content = f"[bold]{article.titulo}[/bold]\n"
                    content += f"[dim]Por {article.autor} • {article.tempo_postagem} • {article.origem}[/dim]\n"
                    content += f"[cyan]💬 {article.comentarios} comentários[/cyan]"
                    
                    console.print(Panel(
                        content,
                        title=f"[{i}]",
                        title_align="left",
                        padding=(0, 1),
                        border_style="blue"
                    ))
                
                console.print("\n[dim]Mostrando as 20 notícias mais recentes[/dim]")
        
        except Exception as e:
            console.print(f"[red]Erro ao carregar notícias: {e}[/red]")
        
        console.print("\n[dim]Pressione Enter para voltar ao menu...[/dim]")
        input()
    
    def add_site(self):
        self.clear_screen()
        self.show_header()
        
        console.print("[bold yellow]➕ Adicionar novo site[/bold yellow]\n")
        
        # Mostrar sites disponíveis
        available = self.config_manager.get_available_sites()
        active = self.config_manager.get_active_sites()
        
        console.print("[bold]Sites disponíveis:[/bold]")
        for site in available:
            status = "[green]✓ Ativo[/green]" if site in active else "[dim]○ Inativo[/dim]"
            console.print(f"  • {site} {status}")
        
        console.print("\n[dim]Digite o nome do site ou 'cancelar' para voltar[/dim]")
        site_name = Prompt.ask("\nSite")
        
        if site_name.lower() != 'cancelar':
            if self.config_manager.add_site(site_name):
                console.print(f"\n[green]✓ Site '{site_name}' adicionado com sucesso![/green]")
            else:
                console.print(f"\n[red]✗ Erro ao adicionar site '{site_name}'[/red]")
        
        console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def remove_site(self):
        self.clear_screen()
        self.show_header()
        
        console.print("[bold yellow]➖ Remover site[/bold yellow]\n")
        
        active_sites = self.config_manager.get_active_sites()
        
        if not active_sites:
            console.print("[red]Nenhum site ativo para remover![/red]")
        else:
            console.print("[bold]Sites ativos:[/bold]")
            for i, site in enumerate(active_sites, 1):
                console.print(f"  {i}. {site}")
            
            console.print("\n[dim]Digite o número do site ou 0 para cancelar[/dim]")
            choice = IntPrompt.ask("\nEscolha", default=0)
            
            if 0 < choice <= len(active_sites):
                site_name = active_sites[choice - 1]
                if self.config_manager.remove_site(site_name):
                    console.print(f"\n[green]✓ Site '{site_name}' removido com sucesso![/green]")
                else:
                    console.print(f"\n[red]✗ Erro ao remover site '{site_name}'[/red]")
        
        console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def list_sites(self):
        self.clear_screen()
        self.show_header()
        
        console.print("[bold yellow]📋 Sites configurados[/bold yellow]\n")
        
        active_sites = self.config_manager.get_active_sites()
        
        if not active_sites:
            console.print("[dim]Nenhum site ativo no momento.[/dim]")
        else:
            table = Table(title="Sites Ativos", box=box.ROUNDED)
            table.add_column("Site", style="cyan")
            table.add_column("Status", style="green")
            
            for site in active_sites:
                table.add_row(site, "✓ Ativo")
            
            console.print(table)
        
        console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def update_news(self):
        self.clear_screen()
        self.show_header()
        
        console.print("[bold yellow]🔄 Atualizando notícias...[/bold yellow]\n")
        
        active_sites = self.config_manager.get_active_sites()
        
        if not active_sites:
            console.print("[red]Nenhum site ativo para atualizar![/red]")
        else:
            for site in active_sites:
                console.print(f"[dim]Atualizando {site}...[/dim]")
                # Aqui você pode adicionar lógica de cache/atualização forçada
            
            console.print(f"\n[green]✓ Atualização concluída![/green]")
        
        console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def run(self):
        while self.running:
            self.clear_screen()
            self.show_header()
            self.show_menu()
            
            choice = Prompt.ask("Escolha uma opção", default="1")
            
            if choice == "1":
                self.show_latest_news()
            elif choice == "2":
                self.add_site()
            elif choice == "3":
                self.remove_site()
            elif choice == "4":
                self.list_sites()
            elif choice == "5":
                self.update_news()
            elif choice == "0":
                self.running = False
                console.print("\n[bold green]Até logo! 👋[/bold green]")
            else:
                console.print("\n[red]Opção inválida![/red]")
                console.print("[dim]Pressione Enter para continuar...[/dim]")
                input()


if __name__ == "__main__":
    try:
        app = WidiaNews()
        app.run()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Programa interrompido pelo usuário[/bold red]")
        sys.exit(0)