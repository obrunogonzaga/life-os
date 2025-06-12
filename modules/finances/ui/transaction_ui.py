"""
Transaction Management UI for Finance Module

This module provides the user interface for managing financial transactions,
including creation, listing, editing, and deletion of transactions.
"""

from datetime import datetime
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
            ("0", "❌ Sair do Sistema"),
            ("M", "🔙 Voltar ao Menu Principal"),
            ("B", "⬅️ Voltar ao Menu Anterior")
        ]
    
    def show_menu(self):
        """Display the transaction management menu"""
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
        
        # Use the standardized menu loop from BaseUI
        result = self.run_menu_loop(
            "📝 Gerenciamento de Transações",
            self.menu_options,
            action_handlers,
            show_navigation=True
        )
        
        return result
    
    def create_transaction(self):
        """Create a new transaction"""
        self.clear()
        header = self.create_header_panel("➕ Criar Nova Transação")
        self.print(header)
        
        try:
            # 1. Escolher tipo de origem (conta ou cartão)
            self.show_info("Selecione o tipo de origem da transação:")
            tipo_origem = self.get_text_input("Digite (1) para Conta ou (2) para Cartão: ")
            
            conta_id = None
            cartao_id = None
            
            if tipo_origem == "1":
                # Listar contas disponíveis
                accounts = self.account_service.list_accounts(active_only=True)
                if not accounts:
                    self.show_error("Nenhuma conta ativa encontrada.")
                    self.wait_for_enter()
                    return
                
                # Mostrar contas
                table = self.create_table(
                    title="Contas Disponíveis",
                    columns=["ID", "Nome", "Banco", "Saldo"]
                )
                
                for i, acc in enumerate(accounts, 1):
                    table.add_row(
                        str(i),
                        acc.nome,
                        acc.banco,
                        f"R$ {acc.saldo_atual:,.2f}"
                    )
                
                self.print(table)
                
                # Selecionar conta
                choice = self.get_text_input("\nDigite o número da conta: ")
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(accounts):
                        conta_id = accounts[index].id
                    else:
                        self.show_error("Número inválido.")
                        self.wait_for_enter()
                        return
                except ValueError:
                    self.show_error("Entrada inválida.")
                    self.wait_for_enter()
                    return
                    
            elif tipo_origem == "2":
                # Listar cartões disponíveis
                cards = self.card_service.list_cards(active_only=True)
                if not cards:
                    self.show_error("Nenhum cartão ativo encontrado.")
                    self.wait_for_enter()
                    return
                
                # Mostrar cartões
                table = self.create_table(
                    title="Cartões Disponíveis",
                    columns=["ID", "Nome", "Banco", "Limite Disponível"]
                )
                
                for i, card in enumerate(cards, 1):
                    table.add_row(
                        str(i),
                        card.nome,
                        card.banco,
                        f"R$ {card.limite_disponivel:,.2f}"
                    )
                
                self.print(table)
                
                # Selecionar cartão
                choice = self.get_text_input("\nDigite o número do cartão: ")
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(cards):
                        cartao_id = cards[index].id
                    else:
                        self.show_error("Número inválido.")
                        self.wait_for_enter()
                        return
                except ValueError:
                    self.show_error("Entrada inválida.")
                    self.wait_for_enter()
                    return
            else:
                self.show_error("Opção inválida.")
                self.wait_for_enter()
                return
            
            # 2. Dados básicos da transação
            self.print("\n")
            self.show_info("Informe os dados da transação:")
            
            # Descrição
            descricao = self.get_text_input("Descrição: ")
            if not descricao:
                self.show_error("Descrição é obrigatória.")
                self.wait_for_enter()
                return
            
            # Valor
            valor_str = self.get_text_input("Valor (R$): ")
            try:
                valor = float(valor_str.replace(',', '.'))
                if valor <= 0:
                    raise ValueError("Valor deve ser positivo")
            except ValueError:
                self.show_error("Valor inválido.")
                self.wait_for_enter()
                return
            
            # Tipo (débito/crédito)
            tipo_str = self.get_text_input("Tipo - (D)ébito ou (C)rédito: ").upper()
            if tipo_str == 'D':
                tipo = TipoTransacao.DEBITO
            elif tipo_str == 'C':
                tipo = TipoTransacao.CREDITO
            else:
                self.show_error("Tipo inválido.")
                self.wait_for_enter()
                return
            
            # Data da transação
            data_str = self.get_text_input("Data (AAAA-MM-DD) ou Enter para hoje: ")
            if not data_str:
                from datetime import datetime
                data_transacao = datetime.now().strftime("%Y-%m-%d")
            else:
                # Validar formato
                try:
                    from datetime import datetime
                    datetime.strptime(data_str, "%Y-%m-%d")
                    data_transacao = data_str
                except ValueError:
                    self.show_error("Formato de data inválido. Use AAAA-MM-DD.")
                    self.wait_for_enter()
                    return
            
            # 3. Categoria
            categorias = ["Alimentação", "Transporte", "Moradia", "Saúde", "Educação", 
                         "Lazer", "Compras", "Salário", "Investimento", "Outros"]
            
            self.print("\n")
            self.show_info("Selecione uma categoria:")
            for i, cat in enumerate(categorias, 1):
                self.print(f"{i}. {cat}")
            
            cat_choice = self.get_text_input("\nNúmero da categoria (ou Enter para pular): ")
            categoria = None
            if cat_choice:
                try:
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categorias):
                        categoria = categorias[cat_index]
                except ValueError:
                    pass
            
            # 4. Parcelamento (apenas para débitos em cartão)
            parcelas = 1
            if cartao_id and tipo == TipoTransacao.DEBITO:
                parcelas_str = self.get_text_input("\nNúmero de parcelas (Enter para 1): ")
                if parcelas_str:
                    try:
                        parcelas = int(parcelas_str)
                        if parcelas < 1:
                            parcelas = 1
                    except ValueError:
                        parcelas = 1
            
            # 5. Compartilhar com Alzi?
            alzi_str = self.get_text_input("\nCompartilhar com Alzi? (S/N): ").upper()
            compartilhado_com_alzi = alzi_str == 'S'
            
            # 6. Observações
            observacoes = self.get_text_input("\nObservações (opcional): ")
            
            # 7. Confirmar transação
            self.print("\n")
            confirmation_panel = self.create_panel(
                f"[bold]Confirmar Transação:[/]\n\n"
                f"Descrição: {descricao}\n"
                f"Valor: R$ {valor:,.2f}\n"
                f"Tipo: {'Débito' if tipo == TipoTransacao.DEBITO else 'Crédito'}\n"
                f"Data: {data_transacao}\n"
                f"Categoria: {categoria or 'Não informada'}\n"
                f"Origem: {'Conta' if conta_id else 'Cartão'}\n"
                f"Parcelas: {parcelas}\n"
                f"Alzi: {'Sim' if compartilhado_com_alzi else 'Não'}"
            )
            self.print(confirmation_panel)
            
            confirmar = self.get_text_input("\nConfirmar transação? (S/N): ").upper()
            
            if confirmar != 'S':
                self.show_info("Transação cancelada.")
                self.wait_for_enter()
                return
            
            # Criar a transação
            transaction = self.transaction_service.create_transaction(
                descricao=descricao,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                categoria=categoria,
                conta_id=conta_id,
                cartao_id=cartao_id,
                parcelas=parcelas,
                observacoes=observacoes if observacoes else None,
                compartilhado_com_alzi=compartilhado_com_alzi
            )
            
            if transaction:
                self.show_success("Transação criada com sucesso!")
                
                # Mostrar informações sobre parcelamento se aplicável
                if parcelas > 1:
                    self.show_info(f"Transação parcelada em {parcelas}x de R$ {valor/parcelas:,.2f}")
                
            else:
                self.show_error("Erro ao criar transação.")
            
        except Exception as e:
            self.show_error(f"Erro ao criar transação: {e}")
        
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