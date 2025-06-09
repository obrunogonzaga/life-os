"""
Transaction Management UI for Finance Module

This module provides the user interface for managing financial transactions,
including creation, listing, editing, and deletion of transactions.
"""

from .base_ui import BaseUI
from ..services.transaction_service import TransactionService
from ..services.account_service import AccountService
from ..services.card_service import CardService
from utils.finance_models import TipoTransacao


class TransactionUI(BaseUI):
    """User interface for transaction management"""
    
    def __init__(self, transaction_service: TransactionService, 
                 account_service: AccountService, card_service: CardService):
        super().__init__()
        self.transaction_service = transaction_service
        self.account_service = account_service
        self.card_service = card_service
        self.menu_options = [
            ("1", "➕ Criar Nova Transação"),
            ("2", "📋 Listar Transações Recentes"),
            ("3", "🔍 Buscar Transações"),
            ("4", "📅 Transações por Período"),
            ("5", "✏️ Editar Transação"),
            ("6", "🗑️ Excluir Transação"),
            ("7", "📊 Resumo de Transações"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
    
    def show_menu(self):
        """Display the transaction management menu"""
        from .main_menu_ui import MainMenuUI
        main_ui = MainMenuUI()
        
        action_handlers = {
            "1": self.create_transaction,
            "2": self.list_recent_transactions,
            "3": self.search_transactions,
            "4": self.list_by_period,
            "5": self.edit_transaction,
            "6": self.delete_transaction,
            "7": self.show_summary
        }
        
        main_ui.run_submenu_loop(
            "📝 Gerenciamento de Transações",
            self.menu_options,
            action_handlers
        )
    
    def create_transaction(self):
        """Create a new transaction (placeholder)"""
        self.clear()
        header = self.create_header_panel("➕ Criar Nova Transação")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.show_info("Aqui será possível:")
        self.print("• Criar transações para contas ou cartões")
        self.print("• Definir parcelamento automático")
        self.print("• Categorizar transações")
        self.print("• Marcar como compartilhada com Alzi")
        self.print("• Validações de saldo e limite")
        
        self.wait_for_enter()
    
    def list_recent_transactions(self):
        """List recent transactions"""
        self.clear()
        header = self.create_header_panel("📋 Transações Recentes")
        self.print(header)
        
        try:
            # Obter transações
            transactions = self.transaction_service.list_transactions()
            
            if not transactions:
                self.show_warning("Nenhuma transação encontrada.")
                self.wait_for_enter()
                return
            
            # Ordenar por data (mais recente primeiro)
            transactions.sort(key=lambda x: x.data_transacao, reverse=True)
            
            # Limitar a 20 transações mais recentes
            transactions = transactions[:20]
            
            # Criar tabela
            table = self.create_table(
                title="Últimas Transações",
                columns=["Data", "Descrição", "Tipo", "Valor", "Categoria", "Conta/Cartão", "Alzi"]
            )
            
            for trans in transactions:
                # Formatar data
                data = trans.data_transacao[:10]  # YYYY-MM-DD
                
                # Tipo colorido
                tipo_str = "[green]Crédito[/]" if trans.tipo == TipoTransacao.CREDITO else "[red]Débito[/]"
                
                # Valor formatado
                valor_str = f"R$ {trans.valor:,.2f}"
                if trans.tipo == TipoTransacao.DEBITO:
                    valor_str = f"[red]-{valor_str}[/]"
                else:
                    valor_str = f"[green]+{valor_str}[/]"
                
                # Origem (conta ou cartão)
                origem = ""
                if trans.conta_id:
                    conta = self.account_service.get_account_by_id(trans.conta_id)
                    if conta:
                        origem = f"Conta: {conta.nome}"
                elif trans.cartao_id:
                    cartao = self.card_service.get_card_by_id(trans.cartao_id)
                    if cartao:
                        origem = f"Cartão: {cartao.nome}"
                
                # Flag Alzi
                alzi_str = "✓" if trans.compartilhado_com_alzi else "-"
                
                table.add_row(
                    data,
                    trans.descricao[:40] + ("..." if len(trans.descricao) > 40 else ""),
                    tipo_str,
                    valor_str,
                    trans.categoria or "-",
                    origem,
                    alzi_str
                )
            
            self.print(table)
            
            # Resumo
            self.print("\n")
            summary_panel = self.create_panel(
                f"[bold]Total de transações mostradas:[/] {len(transactions)}"
            )
            self.print(summary_panel)
            
        except Exception as e:
            self.show_error(f"Erro ao listar transações: {e}")
        
        self.wait_for_enter()
    
    def search_transactions(self):
        """Search transactions (placeholder)"""
        self.clear()
        header = self.create_header_panel("🔍 Buscar Transações")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def list_by_period(self):
        """List transactions by period (placeholder)"""
        self.clear()
        header = self.create_header_panel("📅 Transações por Período")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def edit_transaction(self):
        """Edit transaction (placeholder)"""
        self.clear()
        header = self.create_header_panel("✏️ Editar Transação")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def delete_transaction(self):
        """Delete transaction (placeholder)"""
        self.clear()
        header = self.create_header_panel("🗑️ Excluir Transação")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()
    
    def show_summary(self):
        """Show transaction summary (placeholder)"""
        self.clear()
        header = self.create_header_panel("📊 Resumo de Transações")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()