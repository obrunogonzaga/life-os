"""
Alzi Shared Expenses UI for Finance Module

This module provides the user interface for managing shared expenses
with Alzi, including monthly views, calculations, and reports.
"""

from .base_ui import BaseUI
from ..services.alzi_service import AlziService
from datetime import datetime


class AlziUI(BaseUI):
    """User interface for Alzi shared expenses management"""
    
    def __init__(self, alzi_service: AlziService):
        super().__init__()
        self.alzi_service = alzi_service
        self.menu_options = [
            ("1", "👁️ Visualizar Gastos do Mês Atual"),
            ("2", "📅 Visualizar Gastos por Período"),
            ("3", "📊 Relatório Detalhado"),
            ("4", "📈 Histórico Anual"),
            ("5", "⚖️ Calcular Acerto de Contas"),
            ("6", "🔄 Marcar/Desmarcar Transações"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
    
    def show_menu(self):
        """Display the Alzi shared expenses menu"""
        from .main_menu_ui import MainMenuUI
        main_ui = MainMenuUI()
        
        action_handlers = {
            "1": self.show_current_month,
            "2": self.show_by_period,
            "3": self.show_detailed_report,
            "4": self.show_annual_history,
            "5": self.calculate_settlement,
            "6": self.manage_shared_flags
        }
        
        main_ui.run_submenu_loop(
            "👫 Transações Compartilhadas com Alzi",
            self.menu_options,
            action_handlers
        )
    
    def show_current_month(self):
        """Show current month shared expenses"""
        self.clear()
        header = self.create_header_panel("👁️ Gastos Compartilhados - Mês Atual")
        self.print(header)
        
        try:
            summary = self.alzi_service.get_current_month_summary()
            self._display_monthly_summary(summary)
            
        except Exception as e:
            self.handle_exception(e, "visualização do mês atual")
        
        self.wait_for_enter()
    
    def show_by_period(self):
        """Show shared expenses for a specific period"""
        self.clear()
        header = self.create_header_panel("📅 Gastos por Período")
        self.print(header)
        
        try:
            # Get period from user
            hoje = datetime.now()
            ano = self.get_int_input(f"Ano [{hoje.year}]", default=hoje.year, min_value=2020, max_value=2030)
            mes = self.get_int_input(f"Mês [{hoje.month}]", default=hoje.month, min_value=1, max_value=12)
            
            summary = self.alzi_service.get_shared_transactions_summary(ano, mes)
            self._display_monthly_summary(summary)
            
        except Exception as e:
            self.handle_exception(e, "visualização por período")
        
        self.wait_for_enter()
    
    def show_detailed_report(self):
        """Show comprehensive detailed report"""
        self.clear()
        header = self.create_header_panel("📊 Relatório Detalhado")
        self.print(header)
        
        try:
            # Get period from user
            hoje = datetime.now()
            ano = self.get_int_input(f"Ano [{hoje.year}]", default=hoje.year, min_value=2020, max_value=2030)
            mes = self.get_int_input(f"Mês [{hoje.month}]", default=hoje.month, min_value=1, max_value=12)
            
            report = self.alzi_service.get_comprehensive_shared_report(ano, mes)
            self._display_comprehensive_report(report)
            
        except Exception as e:
            self.handle_exception(e, "relatório detalhado")
        
        self.wait_for_enter()
    
    def show_annual_history(self):
        """Show annual history of shared expenses"""
        self.clear()
        header = self.create_header_panel("📈 Histórico Anual")
        self.print(header)
        
        try:
            # Get year from user
            hoje = datetime.now()
            ano = self.get_int_input(f"Ano [{hoje.year}]", default=hoje.year, min_value=2020, max_value=2030)
            
            annual_summary = self.alzi_service.get_year_shared_summary(ano)
            self._display_annual_summary(annual_summary)
            
        except Exception as e:
            self.handle_exception(e, "histórico anual")
        
        self.wait_for_enter()
    
    def calculate_settlement(self):
        """Calculate settlement between Bruno and Alzi"""
        self.clear()
        header = self.create_header_panel("⚖️ Acerto de Contas")
        self.print(header)
        
        try:
            # Get period from user
            hoje = datetime.now()
            ano = self.get_int_input(f"Ano [{hoje.year}]", default=hoje.year, min_value=2020, max_value=2030)
            mes = self.get_int_input(f"Mês [{hoje.month}]", default=hoje.month, min_value=1, max_value=12)
            
            settlement = self.alzi_service.calculate_settlement(ano, mes)
            self._display_settlement(settlement)
            
        except Exception as e:
            self.handle_exception(e, "cálculo de acerto")
        
        self.wait_for_enter()
    
    def manage_shared_flags(self):
        """Manage shared transaction flags (placeholder)"""
        self.clear()
        header = self.create_header_panel("🔄 Gerenciar Marcações")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.show_info("Aqui será possível:")
        self.print("• Marcar transações como compartilhadas")
        self.print("• Desmarcar transações compartilhadas")
        self.print("• Operações em lote")
        self.print("• Filtros avançados")
        
        self.wait_for_enter()
    
    def _display_monthly_summary(self, summary):
        """Display monthly summary information"""
        self.print_newline()
        
        # Main summary panel
        summary_content = (
            f"[bold]Período:[/bold] {summary['periodo']}\n"
            f"[bold]Total de Transações:[/bold] {summary['total_transacoes']}\n"
            f"[bold]Total de Débitos:[/bold] {self.format_currency(summary['total_debitos'])}\n"
            f"[bold]Total de Créditos:[/bold] {self.format_currency(summary['total_creditos'])}\n"
            f"[bold]Saldo Líquido:[/bold] {self.format_currency(summary['saldo_liquido_compartilhado'])}\n\n"
            f"[bold red]💰 Divisão 50/50[/bold red]\n"
            f"[bold]Valor Individual:[/bold] {self.format_currency(summary['valor_individual'])}\n"
            f"[bold]Bruno deve pagar:[/bold] {self.format_currency(summary['valor_bruno'])}\n"
            f"[bold]Alzi deve pagar:[/bold] {self.format_currency(summary['valor_alzi'])}"
        )
        
        summary_panel = self.create_info_panel(summary_content, f"Resumo - {summary['periodo']}")
        self.print(summary_panel)
        
        # Categories breakdown
        if summary['transacoes_por_categoria']:
            self.print_newline()
            self.print("[bold cyan]📊 Gastos por Categoria[/bold cyan]")
            
            columns = [
                ("Categoria", "cyan", 20),
                ("Transações", "yellow", 12),
                ("Valor Total", "green", 15),
                ("Valor Individual", "blue", 15)
            ]
            
            data = []
            for categoria, info in summary['transacoes_por_categoria'].items():
                data.append([
                    categoria,
                    str(info['count']),
                    self.format_currency(info['total']),
                    self.format_currency(info['valor_individual'])
                ])
            
            table = self.create_data_table(columns, data, "Breakdown por Categoria")
            self.print(table)
        
        # Account/Card breakdown
        if summary['transacoes_por_conta_cartao']:
            breakdown = summary['transacoes_por_conta_cartao']
            
            if breakdown.get('contas'):
                self.print_newline()
                self.print("[bold green]🏦 Gastos por Conta[/bold green]")
                for nome, info in breakdown['contas'].items():
                    self.print(f"• {nome}: {self.format_currency(info['total'])} ({info['count']} transações)")
            
            if breakdown.get('cartoes'):
                self.print_newline()
                self.print("[bold magenta]💳 Gastos por Cartão[/bold magenta]")
                for nome, info in breakdown['cartoes'].items():
                    self.print(f"• {nome}: {self.format_currency(info['total'])} ({info['count']} transações)")
    
    def _display_comprehensive_report(self, report):
        """Display comprehensive report information"""
        self.print_newline()
        
        # General summary
        resumo = report['resumo_geral']
        general_content = (
            f"[bold]Período:[/bold] {report['periodo']}\n"
            f"[bold]Total Gasto Compartilhado:[/bold] {self.format_currency(resumo['total_gasto_compartilhado'])}\n"
            f"[bold]Valor Individual:[/bold] {self.format_currency(resumo['valor_individual'])}\n"
            f"[bold]% do Orçamento:[/bold] {self.format_percentage(resumo['percentual_do_orcamento'])}"
        )
        
        # Previous month comparison
        if resumo.get('comparacao_mes_anterior'):
            comp = resumo['comparacao_mes_anterior']
            general_content += f"\n\n[bold]📈 Comparação com Mês Anterior[/bold]\n"
            general_content += f"Mês anterior: {self.format_currency(comp['mes_anterior'])}\n"
            general_content += f"Diferença: {self.format_currency(comp['diferenca'])}\n"
            general_content += f"Variação: {self.format_percentage(comp['percentual_variacao'])}\n"
            general_content += f"Tendência: {comp['tendencia'].title()}"
        
        summary_panel = self.create_info_panel(general_content, f"Relatório Completo - {report['periodo']}")
        self.print(summary_panel)
        
        # Insights
        if report.get('insights'):
            self.print_newline()
            self.print("[bold yellow]💡 Insights[/bold yellow]")
            for insight in report['insights']:
                self.print(f"• {insight}")
        
        # Highest transactions
        if report['transacoes_detalhadas'].get('maiores_gastos'):
            self.print_newline()
            self.print("[bold red]🔥 Maiores Gastos[/bold red]")
            
            columns = [
                ("Descrição", "white", 25),
                ("Valor", "red", 12),
                ("Individual", "blue", 12),
                ("Data", "green", 12),
                ("Categoria", "yellow", 15)
            ]
            
            data = []
            for gasto in report['transacoes_detalhadas']['maiores_gastos'][:10]:
                data.append([
                    gasto['descricao'][:24],
                    self.format_currency(gasto['valor']),
                    self.format_currency(gasto['valor_individual']),
                    gasto['data'],
                    gasto['categoria'][:14]
                ])
            
            table = self.create_data_table(columns, data, "Top 10 Maiores Gastos")
            self.print(table)
    
    def _display_annual_summary(self, annual):
        """Display annual summary information"""
        self.print_newline()
        
        # Annual totals
        annual_content = (
            f"[bold]Ano:[/bold] {annual['ano']}\n"
            f"[bold]Total de Débitos:[/bold] {self.format_currency(annual['total_debitos'])}\n"
            f"[bold]Total de Créditos:[/bold] {self.format_currency(annual['total_creditos'])}\n"
            f"[bold]Saldo Líquido:[/bold] {self.format_currency(annual['saldo_liquido_compartilhado'])}\n\n"
            f"[bold red]💰 Divisão Anual 50/50[/bold red]\n"
            f"[bold]Valor Individual:[/bold] {self.format_currency(annual['valor_individual_ano'])}\n"
            f"[bold]Bruno (total):[/bold] {self.format_currency(annual['valor_bruno_ano'])}\n"
            f"[bold]Alzi (total):[/bold] {self.format_currency(annual['valor_alzi_ano'])}\n"
            f"[bold]Média Mensal:[/bold] {self.format_currency(annual['media_mensal'])}"
        )
        
        # Best/worst months
        if annual.get('mes_maior_gasto'):
            maior = annual['mes_maior_gasto']
            annual_content += f"\n\n[bold]📈 Mês com Maior Gasto:[/bold] {maior['periodo']} - {self.format_currency(maior['total_debitos'])}"
        
        if annual.get('mes_menor_gasto'):
            menor = annual['mes_menor_gasto']
            annual_content += f"\n[bold]📉 Mês com Menor Gasto:[/bold] {menor['periodo']} - {self.format_currency(menor['total_debitos'])}"
        
        summary_panel = self.create_info_panel(annual_content, f"Resumo Anual - {annual['ano']}")
        self.print(summary_panel)
        
        # Monthly breakdown table
        if annual.get('resumos_mensais'):
            self.print_newline()
            self.print("[bold cyan]📅 Breakdown Mensal[/bold cyan]")
            
            columns = [
                ("Mês", "cyan", 8),
                ("Transações", "yellow", 12),
                ("Débitos", "red", 15),
                ("Individual", "blue", 15)
            ]
            
            data = []
            for resumo in annual['resumos_mensais']:
                if resumo['total_transacoes'] > 0:  # Only show months with transactions
                    data.append([
                        resumo['periodo'],
                        str(resumo['total_transacoes']),
                        self.format_currency(resumo['total_debitos']),
                        self.format_currency(resumo['valor_individual'])
                    ])
            
            if data:
                table = self.create_data_table(columns, data, f"Gastos Mensais - {annual['ano']}")
                self.print(table)
    
    def _display_settlement(self, settlement):
        """Display settlement calculation"""
        self.print_newline()
        
        settlement_content = (
            f"[bold]Período:[/bold] {settlement['periodo']}\n"
            f"[bold]Valor Total Gasto:[/bold] {self.format_currency(settlement['valor_total_gasto'])}\n"
            f"[bold]Método de Divisão:[/bold] {settlement['metodo_divisao']}\n\n"
            f"[bold green]💰 Valores a Pagar[/bold green]\n"
            f"[bold]Bruno deve pagar:[/bold] {self.format_currency(settlement['valor_bruno'])}\n"
            f"[bold]Alzi deve pagar:[/bold] {self.format_currency(settlement['valor_alzi'])}\n\n"
            f"[bold]Observações:[/bold] {settlement['observacoes']}"
        )
        
        settlement_panel = self.create_info_panel(settlement_content, f"Acerto de Contas - {settlement['periodo']}")
        self.print(settlement_panel)
        
        # Category breakdown for settlement
        if settlement.get('detalhamento'):
            self.print_newline()
            self.print("[bold yellow]📊 Detalhamento por Categoria[/bold yellow]")
            
            for categoria, info in settlement['detalhamento'].items():
                individual_value = info['total'] / 2
                self.print(f"• {categoria}: {self.format_currency(info['total'])} → {self.format_currency(individual_value)} cada")