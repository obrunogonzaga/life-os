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

# Adicionar o diretório pai ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_manager import ConfigManager
from utils.news_aggregator import NewsAggregator
from scrapers.tabnews_scraper import Artigo, ArtigoDetalhado, Comentario, TabNewsScraper


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
            "[bold cyan]📰 MÓDULO DE NOTÍCIAS[/bold cyan]\n"
            "[dim]Agregador de notícias de tecnologia[/dim]",
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
        table.add_row("6", "📊 Estatísticas do banco")
        table.add_row("0", "⬅️  Voltar ao Life OS")
        
        console.print(table)
        console.print()
    
    def show_latest_news(self):
        try:
            articles = self.news_aggregator.get_all_news()
            
            if not articles:
                self.clear_screen()
                self.show_header()
                console.print("[red]Nenhuma notícia encontrada![/red]")
                console.print("[dim]Verifique se há sites ativos ou tente atualizar.[/dim]")
                console.print("\n[dim]Pressione Enter para voltar ao menu...[/dim]")
                input()
                return
                
            # Implementar paginação
            self.paginated_news_view(articles)
            
        except Exception as e:
            self.clear_screen()
            self.show_header()
            console.print(f"[red]Erro ao carregar notícias: {e}[/red]")
            console.print("\n[dim]Pressione Enter para voltar ao menu...[/dim]")
            input()
    
    def paginated_news_view(self, articles):
        per_page = 5  # Notícias por página
        total_pages = (len(articles) + per_page - 1) // per_page
        current_page = 0
        
        while True:
            self.clear_screen()
            self.show_header()
            
            # Mostrar informações da página
            start_idx = current_page * per_page
            end_idx = min(start_idx + per_page, len(articles))
            
            console.print(f"[green]📰 Notícias {start_idx + 1}-{end_idx} de {len(articles)} "
                         f"(Página {current_page + 1}/{total_pages})[/green]\n")
            
            # Mostrar notícias da página atual
            for i, article in enumerate(articles[start_idx:end_idx], start_idx + 1):
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
            
            # Mostrar controles de navegação
            self.show_navigation_controls(current_page, total_pages)
            
            # Processar input do usuário
            choice = Prompt.ask("\nControle", default="s").lower()
            
            if choice in ['s', 'sair', '0']:
                break
            elif choice in ['p', 'proximo', '>'] and current_page < total_pages - 1:
                current_page += 1
            elif choice in ['a', 'anterior', '<'] and current_page > 0:
                current_page -= 1
            elif choice in ['f', 'final']:
                current_page = total_pages - 1
            elif choice in ['i', 'inicio']:
                current_page = 0
            elif choice.isdigit():
                # Usuário digitou um número - quer ver o artigo
                article_num = int(choice)
                start_idx = current_page * per_page
                if 1 <= article_num <= len(articles):
                    selected_article = articles[article_num - 1]
                    self.show_article_detail(selected_article)
    
    def show_navigation_controls(self, current_page, total_pages):
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))
        table.add_column("Comando", style="cyan", width=12)
        table.add_column("Ação", style="white")
        
        # Navegação condicional
        if current_page > 0:
            table.add_row("A / <", "🔙 Página anterior")
            table.add_row("I", "⏮️  Primeira página")
        
        if current_page < total_pages - 1:
            table.add_row("P / >", "▶️  Próxima página")
            table.add_row("F", "⏭️  Última página")
        
        table.add_row("1-N", "📖 Ver artigo (digite o número)")
        table.add_row("S / 0", "❌ Sair")
        
        console.print("\n[bold]Navegação:[/bold]")
        console.print(table)
    
    def show_article_detail(self, artigo: Artigo):
        """
        Mostra os detalhes completos de um artigo
        """
        self.clear_screen()
        self.show_header()
        
        console.print(f"[bold yellow]📖 Carregando artigo...[/bold yellow]")
        console.print(f"[dim]{artigo.titulo}[/dim]\n")
        
        # Usar o scraper para obter detalhes completos
        scraper = TabNewsScraper()
        artigo_detalhado = scraper.scrape_artigo_detalhado(artigo.link)
        
        if not artigo_detalhado:
            console.print("[red]❌ Erro ao carregar o artigo![/red]")
            console.print("[dim]Pressione Enter para voltar...[/dim]")
            input()
            return
        
        # Exibir detalhes do artigo
        self._display_article_content(artigo_detalhado)
    
    def _display_article_content(self, artigo: ArtigoDetalhado):
        """
        Exibe o conteúdo detalhado do artigo com navegação
        """
        while True:
            self.clear_screen()
            self.show_header()
            
            # Cabeçalho do artigo
            header_content = f"[bold]{artigo.titulo}[/bold]\n"
            header_content += f"[dim]Por {artigo.autor} • {artigo.tempo_postagem} • {artigo.origem}[/dim]"
            
            console.print(Panel(
                header_content,
                border_style="blue",
                padding=(1, 2)
            ))
            
            # Menu de opções
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Opção", style="cyan", width=8)
            table.add_column("Ação", style="white")
            
            table.add_row("1", "📄 Ver conteúdo")
            table.add_row("2", f"💬 Ver comentários ({len(artigo.comentarios)})")
            table.add_row("3", "🔗 Copiar link")
            table.add_row("0", "⬅️  Voltar")
            
            console.print(table)
            
            choice = Prompt.ask("\nEscolha uma opção", default="1")
            
            if choice == "1":
                self._show_article_content(artigo)
            elif choice == "2":
                self._show_article_comments(artigo)
            elif choice == "3":
                console.print(f"\n[green]📋 Link copiado:[/green]")
                console.print(f"[dim]{artigo.link}[/dim]")
                console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
            elif choice == "0":
                break
            else:
                console.print("\n[red]Opção inválida![/red]")
                console.print("[dim]Pressione Enter para continuar...[/dim]")
                input()
    
    def _show_article_content(self, artigo: ArtigoDetalhado):
        """
        Mostra o conteúdo do artigo em formato paginado
        """
        self.clear_screen()
        self.show_header()
        
        # Cabeçalho
        console.print(Panel(
            f"[bold]{artigo.titulo}[/bold]\n"
            f"[dim]Por {artigo.autor} • {artigo.tempo_postagem}[/dim]",
            border_style="blue",
            title="📄 Conteúdo do Artigo"
        ))
        
        # Dividir conteúdo em linhas para paginação
        content_lines = artigo.conteudo_markdown.split('\n')
        lines_per_page = 20
        total_pages = (len(content_lines) + lines_per_page - 1) // lines_per_page
        current_page = 0
        
        while True:
            # Mostrar página atual
            start_idx = current_page * lines_per_page
            end_idx = min(start_idx + lines_per_page, len(content_lines))
            
            console.print(f"\n[dim]Página {current_page + 1} de {total_pages}[/dim]")
            console.print("─" * 60)
            
            for line in content_lines[start_idx:end_idx]:
                console.print(line)
            
            console.print("─" * 60)
            
            # Controles de navegação
            controls = []
            if current_page > 0:
                controls.append("A = Anterior")
            if current_page < total_pages - 1:
                controls.append("P = Próxima")
            controls.append("S = Sair")
            
            console.print(f"[dim]{' | '.join(controls)}[/dim]")
            
            choice = Prompt.ask("\nNavegação", default="s").lower()
            
            if choice in ['s', 'sair']:
                break
            elif choice in ['p', 'proximo'] and current_page < total_pages - 1:
                current_page += 1
                self.clear_screen()
                self.show_header()
                console.print(Panel(
                    f"[bold]{artigo.titulo}[/bold]\n"
                    f"[dim]Por {artigo.autor} • {artigo.tempo_postagem}[/dim]",
                    border_style="blue",
                    title="📄 Conteúdo do Artigo"
                ))
            elif choice in ['a', 'anterior'] and current_page > 0:
                current_page -= 1
                self.clear_screen()
                self.show_header()
                console.print(Panel(
                    f"[bold]{artigo.titulo}[/bold]\n"
                    f"[dim]Por {artigo.autor} • {artigo.tempo_postagem}[/dim]",
                    border_style="blue",
                    title="📄 Conteúdo do Artigo"
                ))
    
    def _show_article_comments(self, artigo: ArtigoDetalhado):
        """
        Mostra os comentários do artigo
        """
        self.clear_screen()
        self.show_header()
        
        console.print(Panel(
            f"[bold]{artigo.titulo}[/bold]\n"
            f"[dim]Por {artigo.autor} • {artigo.tempo_postagem}[/dim]",
            border_style="blue",
            title=f"💬 Comentários ({len(artigo.comentarios)})"
        ))
        
        if not artigo.comentarios:
            console.print("\n[dim]Nenhum comentário encontrado.[/dim]")
        else:
            for i, comentario in enumerate(artigo.comentarios, 1):
                comment_content = f"[bold]{comentario.autor}[/bold]"
                if comentario.tempo_postagem:
                    comment_content += f" [dim]• {comentario.tempo_postagem}[/dim]"
                comment_content += f"\n\n{comentario.conteudo}"
                
                console.print(Panel(
                    comment_content,
                    title=f"Comentário {i}",
                    border_style="green",
                    padding=(1, 2)
                ))
        
        console.print("\n[dim]Pressione Enter para voltar...[/dim]")
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
        
        console.print("[bold yellow]🔄 Forçando atualização de todas as notícias...[/bold yellow]\n")
        
        active_sites = self.config_manager.get_active_sites()
        
        if not active_sites:
            console.print("[red]Nenhum site ativo para atualizar![/red]")
        else:
            console.print("[dim]Isso pode levar alguns segundos...[/dim]\n")
            
            # Usar o método force_update_all do news_aggregator
            success = self.news_aggregator.force_update_all()
            
            if success:
                console.print(f"\n[green]✅ Todas as fontes foram atualizadas com sucesso![/green]")
            else:
                console.print(f"\n[yellow]⚠️  Algumas fontes falharam na atualização[/yellow]")
        
        console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def show_database_stats(self):
        self.clear_screen()
        self.show_header()
        
        console.print("[bold yellow]📊 Estatísticas do Banco de Dados[/bold yellow]\n")
        
        try:
            stats = self.news_aggregator.get_database_stats()
            
            # Status da conexão MongoDB
            mongodb_status = "🟢 Conectado" if stats.get("mongodb_connected") else "🔴 Desconectado (usando fallback JSON)"
            console.print(f"[bold]MongoDB:[/bold] {mongodb_status}\n")
            
            # Estatísticas por fonte
            sources = stats.get("sources", {})
            
            if sources:
                table = Table(title="Estatísticas por Fonte", box=box.ROUNDED)
                table.add_column("Fonte", style="cyan")
                table.add_column("Última Atualização", style="yellow")
                table.add_column("Total de Artigos", style="green")
                table.add_column("Status", style="white")
                
                for source, source_stats in sources.items():
                    last_update = source_stats.get('ultimo_update')
                    total_articles = source_stats.get('total_articles', 0)
                    
                    if last_update:
                        # Calcular diferença de tempo
                        from datetime import datetime, timedelta
                        time_diff = datetime.now() - last_update
                        hours_ago = time_diff.total_seconds() / 3600
                        
                        if hours_ago < 1:
                            update_str = f"{int(time_diff.total_seconds() / 60)} min atrás"
                            status = "🟢 Atualizado"
                        elif hours_ago < 6:
                            update_str = f"{hours_ago:.1f}h atrás"
                            status = "🟡 Recente"
                        else:
                            update_str = f"{hours_ago:.1f}h atrás"
                            status = "🔴 Desatualizado"
                        
                        last_update_str = last_update.strftime("%d/%m %H:%M")
                    else:
                        update_str = "Nunca"
                        last_update_str = "N/A"
                        status = "⚪ Não inicializado"
                    
                    table.add_row(
                        source,
                        f"{last_update_str}\n[dim]{update_str}[/dim]",
                        str(total_articles),
                        status
                    )
                
                console.print(table)
            else:
                console.print("[dim]Nenhuma estatística disponível.[/dim]")
            
            # Informações adicionais
            console.print(f"\n[bold]Configurações:[/bold]")
            console.print(f"• Intervalo de atualização: 6 horas")
            console.print(f"• Máximo de artigos por fonte: {self.config_manager.get_max_articles()}")
            console.print(f"• Sites ativos: {', '.join(self.config_manager.get_active_sites())}")
            
        except Exception as e:
            console.print(f"[red]❌ Erro ao obter estatísticas: {e}[/red]")
        
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
            elif choice == "6":
                self.show_database_stats()
            elif choice == "0":
                self.running = False
                console.print("\n[dim]Voltando ao menu principal...[/dim]")
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