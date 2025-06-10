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
            ("5", "💳 Faturas de Cartão"),
            ("6", "✏️ Editar Transação"),
            ("7", "🗑️ Excluir Transação"),
            ("8", "📊 Resumo de Transações"),
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
            "5": self.show_card_invoices,
            "6": self.edit_transaction,
            "7": self.delete_transaction,
            "8": self.show_summary
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
    
    def show_card_invoices(self):
        """Show credit card invoices grouped by month"""
        self.clear()
        header = self.create_header_panel("💳 Faturas de Cartão")
        self.print(header)
        
        try:
            # Listar cartões disponíveis
            cards = self.card_service.list_cards(active_only=True)
            if not cards:
                self.show_warning("Nenhum cartão de crédito cadastrado.")
                self.wait_for_enter()
                return
            
            # Mostrar cartões para seleção
            self.show_info("Selecione um cartão para visualizar as faturas:")
            
            table = self.create_table(
                title="Cartões Disponíveis",
                columns=["ID", "Nome", "Banco", "Fechamento", "Vencimento"]
            )
            
            for i, card in enumerate(cards, 1):
                table.add_row(
                    str(i),
                    card.nome,
                    card.banco,
                    f"Dia {card.dia_fechamento}",
                    f"Dia {card.dia_vencimento}"
                )
            
            self.print(table)
            
            # Solicitar seleção
            choice = self.get_text_input("\nDigite o número do cartão (ou 'C' para cancelar): ")
            
            if choice.upper() == 'C':
                return
                
            try:
                index = int(choice) - 1
                if 0 <= index < len(cards):
                    selected_card = cards[index]
                    self._show_invoice_details(selected_card.id)
                else:
                    self.show_error("Número inválido.")
                    self.wait_for_enter()
            except ValueError:
                self.show_error("Entrada inválida.")
                self.wait_for_enter()
                
        except Exception as e:
            self.show_error(f"Erro ao mostrar faturas: {e}")
            self.wait_for_enter()
    
    def _show_invoice_details(self, card_id: str):
        """Show detailed invoices for a specific card"""
        self.clear()
        
        try:
            # Obter resumo de faturas dos últimos 6 meses
            summary = self.transaction_service.get_card_invoices_summary(card_id)
            
            header = self.create_header_panel(f"💳 Faturas - {summary['card_name']}")
            self.print(header)
            
            # Informações do cartão
            info_panel = self.create_panel(
                f"[bold]Fechamento:[/] Dia {summary['closing_day']}  |  "
                f"[bold]Vencimento:[/] Dia {summary['due_day']}"
            )
            self.print(info_panel)
            self.print("")
            
            # Criar tabela com resumo das faturas
            table = self.create_table(
                title="Resumo das Faturas (últimos 3 meses + próximos 2 meses)",
                columns=["Mês/Ano", "Qtd Trans.", "Débitos", "Créditos", "Total Fatura"]
            )
            
            for key in sorted(summary['invoices'].keys(), reverse=True):
                invoice = summary['invoices'][key]
                
                # Formatar valores
                debitos_str = f"R$ {invoice['total_debits']:,.2f}"
                creditos_str = f"R$ {invoice['total_credits']:,.2f}" if invoice['total_credits'] > 0 else "-"
                total_str = f"R$ {invoice['net_amount']:,.2f}"
                
                # Colorir total
                if invoice['net_amount'] > 0:
                    total_str = f"[red]{total_str}[/]"
                
                table.add_row(
                    f"{invoice['month_name'][:3]}/{invoice['year']}",
                    str(invoice['total_transactions']),
                    debitos_str,
                    creditos_str,
                    total_str
                )
            
            self.print(table)
            self.print("")
            
            # Opção para ver detalhes de uma fatura específica
            choice = self.get_text_input("Digite o mês/ano (MM/AAAA) para ver detalhes ou 'V' para voltar: ")
            
            if choice.upper() != 'V':
                try:
                    month, year = map(int, choice.split('/'))
                    key = f"{year}-{month:02d}"
                    
                    if key in summary['invoices']:
                        self._show_invoice_transactions(card_id, month, year, summary['invoices'][key])
                    else:
                        self.show_error("Mês/ano não encontrado.")
                        self.wait_for_enter()
                except:
                    self.show_error("Formato inválido. Use MM/AAAA.")
                    self.wait_for_enter()
                    
        except Exception as e:
            self.show_error(f"Erro ao obter faturas: {e}")
            self.wait_for_enter()
    
    def _show_invoice_transactions(self, card_id: str, month: int, year: int, invoice_data: dict):
        """Show detailed transactions for a specific invoice"""
        self.clear()
        
        header = self.create_header_panel(
            f"💳 Fatura Detalhada - {invoice_data['month_name']}/{year}"
        )
        self.print(header)
        
        if not invoice_data['transactions']:
            self.show_info("Nenhuma transação nesta fatura.")
            self.wait_for_enter()
            return
        
        # Criar tabela de transações
        table = self.create_table(
            title="Transações da Fatura",
            columns=["Data", "Descrição", "Categoria", "Valor", "Parcela", "Alzi"]
        )
        
        # Ordenar transações por data
        transactions = sorted(invoice_data['transactions'], 
                            key=lambda x: x.data_transacao)
        
        for trans in transactions:
            # Formatar data
            data = trans.data_transacao[:10]
            
            # Formatar valor
            valor_str = f"R$ {trans.valor:,.2f}"
            if trans.tipo == TipoTransacao.DEBITO:
                valor_str = f"[red]{valor_str}[/]"
            else:
                valor_str = f"[green]+{valor_str}[/]"
            
            # Info de parcela
            parcela_str = "-"
            if trans.parcelamento:
                for p in trans.parcelamento:
                    if p.data_vencimento[:7] == f"{year}-{month:02d}":
                        parcela_str = f"{p.numero_parcela}/{p.total_parcelas}"
                        break
            
            # Flag Alzi
            alzi_str = "✓" if trans.compartilhado_com_alzi else "-"
            
            table.add_row(
                data,
                trans.descricao[:35] + ("..." if len(trans.descricao) > 35 else ""),
                trans.categoria or "-",
                valor_str,
                parcela_str,
                alzi_str
            )
        
        self.print(table)
        self.print("")
        
        # Resumo da fatura
        summary_panel = self.create_panel(
            f"[bold]Total de transações:[/] {invoice_data['total_transactions']}  |  "
            f"[bold]Total débitos:[/] R$ {invoice_data['total_debits']:,.2f}  |  "
            f"[bold]Total créditos:[/] R$ {invoice_data['total_credits']:,.2f}  |  "
            f"[bold red]Total fatura:[/] R$ {invoice_data['net_amount']:,.2f}"
        )
        self.print(summary_panel)
        
        self.wait_for_enter()
    
    def show_summary(self):
        """Show transaction summary (placeholder)"""
        self.clear()
        header = self.create_header_panel("📊 Resumo de Transações")
        self.print(header)
        
        self.show_info("Funcionalidade em desenvolvimento")
        self.wait_for_enter()