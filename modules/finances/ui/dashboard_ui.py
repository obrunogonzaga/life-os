"""
Dashboard UI for Finance Module

This module provides the dashboard interface showing financial summaries,
overviews, and key metrics for the finance module.
"""

from .base_ui import BaseUI
from ..services.finance_service import FinanceService


class DashboardUI(BaseUI):
    """Dashboard interface for financial overview"""
    
    def __init__(self, finance_service: FinanceService):
        super().__init__()
        self.finance_service = finance_service
    
    def show_dashboard(self):
        """Display the main financial dashboard"""
        self.clear()
        header = self.create_header_panel("📊 Dashboard Financeiro")
        self.print(header)
        
        try:
            # Get financial summary
            resumo = self.finance_service.obter_resumo_financeiro()
            
            # Create layout
            layout = self.create_dashboard_layout()
            
            # Header section
            layout["header"].update(header)
            
            # Body section with two columns
            body_layout = self.create_two_column_layout()
            
            # Left column - Account/Card summaries
            left_content = self._create_accounts_cards_summary(resumo)
            body_layout["left"].update(left_content)
            
            # Right column - Transaction summaries
            right_content = self._create_transactions_summary(resumo)
            body_layout["right"].update(right_content)
            
            layout["body"].update(body_layout)
            
            # Footer with navigation
            footer_panel = self.create_info_panel(
                "[dim]Pressione Enter para voltar ao menu...[/dim]",
                style="dim"
            )
            layout["footer"].update(footer_panel)
            
            self.print(layout)
            
        except Exception as e:
            self.handle_exception(e, "dashboard")
            self._show_simple_dashboard()
        
        self.wait_for_enter()
    
    def _create_accounts_cards_summary(self, resumo) -> str:
        """Create accounts and cards summary section"""
        content = []
        
        # Accounts section
        content.append("[bold cyan]🏦 Contas Correntes[/bold cyan]")
        content.append(f"Total de contas: {resumo.total_contas}")
        content.append(f"Contas compartilhadas: {resumo.contas_compartilhadas}")
        content.append(f"Saldo total: {self.format_currency(resumo.saldo_total_contas)}")
        content.append("")
        
        # Cards section
        content.append("[bold magenta]💳 Cartões de Crédito[/bold magenta]")
        content.append(f"Total de cartões: {resumo.total_cartoes}")
        content.append(f"Cartões compartilhados: {resumo.cartoes_compartilhados}")
        content.append(f"Limite total: {self.format_currency(resumo.limite_total_cartoes)}")
        content.append(f"Limite disponível: {self.format_currency(resumo.limite_disponivel_cartoes)}")
        content.append(f"Limite usado: {self.format_currency(resumo.limite_total_cartoes - resumo.limite_disponivel_cartoes)}")
        
        usage_percent = 0
        if resumo.limite_total_cartoes > 0:
            usage_percent = ((resumo.limite_total_cartoes - resumo.limite_disponivel_cartoes) / resumo.limite_total_cartoes) * 100
        content.append(f"Uso do limite: {self.format_percentage(usage_percent)}")
        
        return self.create_info_panel("\n".join(content), "Resumo de Contas e Cartões")
    
    def _create_transactions_summary(self, resumo) -> str:
        """Create transactions summary section"""
        content = []
        
        # Current month transactions
        content.append("[bold green]📝 Transações do Mês[/bold green]")
        content.append(f"Total de transações: {resumo.total_transacoes}")
        content.append(f"Valor total de gastos: {self.format_currency(resumo.valor_total_gastos_mes)}")
        content.append("")
        
        # Shared expenses with Alzi
        content.append("[bold red]👫 Gastos Compartilhados (Alzi)[/bold red]")
        content.append(f"Transações compartilhadas: {resumo.transacoes_compartilhadas_mes}")
        content.append(f"Valor compartilhado: {self.format_currency(resumo.valor_compartilhado_alzi_mes)}")
        content.append(f"Valor individual: {self.format_currency(resumo.valor_compartilhado_alzi_mes / 2)}")
        
        if resumo.valor_total_gastos_mes > 0:
            shared_percent = (resumo.valor_compartilhado_alzi_mes / resumo.valor_total_gastos_mes) * 100
            content.append(f"% do total: {self.format_percentage(shared_percent)}")
        
        return self.create_info_panel("\n".join(content), "Resumo de Transações")
    
    def _show_simple_dashboard(self):
        """Show a simplified dashboard in case of errors"""
        self.clear()
        header = self.create_header_panel("📊 Dashboard Financeiro")
        self.print(header)
        
        self.show_warning("Erro ao carregar dados completos. Exibindo informações básicas.")
        
        try:
            # Try to get basic information
            accounts = self.finance_service.account_service.list_accounts()
            cards = self.finance_service.card_service.list_cards()
            
            self.print_newline()
            self.show_info(f"Contas cadastradas: {len(accounts)}")
            self.show_info(f"Cartões cadastrados: {len(cards)}")
            
            if accounts:
                total_balance = sum(acc.saldo_atual for acc in accounts if acc.ativa)
                self.show_info(f"Saldo total das contas: {self.format_currency(total_balance)}")
            
            if cards:
                total_limit = sum(card.limite for card in cards if card.ativo)
                total_available = sum(card.limite_disponivel for card in cards if card.ativo)
                self.show_info(f"Limite total dos cartões: {self.format_currency(total_limit)}")
                self.show_info(f"Limite disponível: {self.format_currency(total_available)}")
                
        except Exception:
            self.show_error("Não foi possível carregar os dados do dashboard")
    
    def show_statistics(self):
        """Show advanced statistics (placeholder)"""
        self.clear()
        header = self.create_header_panel("📊 Estatísticas Avançadas")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.show_info("Aqui serão exibidas estatísticas detalhadas:")
        self.print("• Gráficos de gastos por categoria")
        self.print("• Tendências mensais")
        self.print("• Comparações período a período")
        self.print("• Análises de padrões de gasto")
        self.print("• Projeções financeiras")
        
        self.wait_for_enter()
    
    def show_reports(self):
        """Show reports (placeholder)"""
        self.clear()
        header = self.create_header_panel("📈 Relatórios e Análises")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.show_info("Aqui serão exibidos relatórios:")
        self.print("• Relatório mensal de gastos")
        self.print("• Relatório anual comparativo")
        self.print("• Análise de cartões por fatura")
        self.print("• Relatório de gastos compartilhados")
        self.print("• Análise de fluxo de caixa")
        
        self.wait_for_enter()