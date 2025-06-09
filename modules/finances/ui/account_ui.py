"""
Account Management UI for Finance Module

This module provides the user interface for managing bank accounts,
including creation, listing, editing, and deletion of accounts.
"""

from typing import List, Optional
from .base_ui import BaseUI
from ..services.account_service import AccountService
from utils.finance_models import ContaCorrente, TipoConta


class AccountUI(BaseUI):
    """User interface for account management"""
    
    def __init__(self, account_service: AccountService):
        super().__init__()
        self.account_service = account_service
        self.menu_options = [
            ("1", "➕ Criar Nova Conta"),
            ("2", "📋 Listar Contas"),
            ("3", "✏️ Editar Conta"),
            ("4", "🗑️ Excluir Conta"),
            ("5", "🔍 Detalhes da Conta"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
    
    def show_menu(self):
        """Display the account management menu"""
        from .main_menu_ui import MainMenuUI
        main_ui = MainMenuUI()
        
        action_handlers = {
            "1": self.create_account,
            "2": self.list_accounts,
            "3": self.edit_account,
            "4": self.delete_account,
            "5": self.show_account_details
        }
        
        main_ui.run_submenu_loop(
            "🏦 Gerenciamento de Contas",
            self.menu_options,
            action_handlers
        )
    
    def create_account(self):
        """Create a new account"""
        self.clear()
        header = self.create_header_panel("➕ Criar Nova Conta")
        self.print(header)
        
        try:
            # Get account details
            nome = self.get_text_input("Nome da conta")
            if not nome:
                self.show_error("Nome da conta é obrigatório")
                self.wait_for_enter()
                return
            
            banco = self.get_text_input("Nome do banco")
            if not banco:
                self.show_error("Nome do banco é obrigatório")
                self.wait_for_enter()
                return
            
            agencia = self.get_text_input("Agência")
            if not agencia:
                self.show_error("Agência é obrigatória")
                self.wait_for_enter()
                return
            
            conta = self.get_text_input("Número da conta")
            if not conta:
                self.show_error("Número da conta é obrigatório")
                self.wait_for_enter()
                return
            
            # Account type selection
            tipo = self.get_enum_choice(
                "Tipo da conta:",
                TipoConta,
                lambda t: t.value.title()
            )
            
            saldo_inicial = self.get_float_input("Saldo inicial", default=0.0, min_value=0.0)
            
            compartilhado = self.get_confirmation("Conta compartilhada com Alzi?", default=False)
            
            # Create account
            account = self.account_service.create_account(
                nome=nome,
                banco=banco,
                agencia=agencia,
                conta=conta,
                tipo=tipo,
                saldo_inicial=saldo_inicial,
                compartilhado_com_alzi=compartilhado
            )
            
            if account:
                self.show_success(f"Conta '{nome}' criada com sucesso!")
                self.show_info(f"ID: {self.format_id(account.id)}")
            else:
                self.show_error("Falha ao criar conta")
            
        except Exception as e:
            self.handle_exception(e, "criação de conta")
        
        self.wait_for_enter()
    
    def list_accounts(self):
        """List all accounts"""
        self.clear()
        header = self.create_header_panel("📋 Lista de Contas")
        self.print(header)
        
        try:
            accounts = self.account_service.list_accounts()
            
            if not accounts:
                self.show_info("Nenhuma conta cadastrada")
                self.wait_for_enter()
                return
            
            # Create table
            columns = [
                ("ID", "cyan", 10),
                ("Nome", "white", 20),
                ("Banco", "yellow", 15),
                ("Agência", "green", 10),
                ("Conta", "blue", 12),
                ("Tipo", "magenta", 12),
                ("Saldo", "white", 15),
                ("Alzi", "red", 6),
                ("Status", "green", 8)
            ]
            
            data = []
            for account in accounts:
                data.append([
                    self.format_id(account.id),
                    account.nome,
                    account.banco,
                    account.agencia,
                    account.conta,
                    account.tipo.value.title(),
                    self.format_currency(account.saldo_atual),
                    self.format_status_icon(account.compartilhado_com_alzi),
                    self.format_status_icon(account.ativa)
                ])
            
            table = self.create_data_table(columns, data, "Contas Cadastradas")
            self.print(table)
            
            # Summary
            total_balance = sum(acc.saldo_atual for acc in accounts if acc.ativa)
            shared_accounts = sum(1 for acc in accounts if acc.compartilhado_com_alzi and acc.ativa)
            
            self.print_newline()
            self.show_info(f"Total de contas: {len(accounts)}")
            self.show_info(f"Contas ativas: {sum(1 for acc in accounts if acc.ativa)}")
            self.show_info(f"Contas compartilhadas: {shared_accounts}")
            self.show_info(f"Saldo total: {self.format_currency(total_balance)}")
            
        except Exception as e:
            self.handle_exception(e, "listagem de contas")
        
        self.wait_for_enter()
    
    def edit_account(self):
        """Edit an existing account"""
        self.clear()
        header = self.create_header_panel("✏️ Editar Conta")
        self.print(header)
        
        try:
            accounts = self.account_service.list_accounts()
            
            if not accounts:
                self.show_info("Nenhuma conta disponível para edição")
                self.wait_for_enter()
                return
            
            # Select account
            account = self.select_from_list(
                accounts,
                "Selecione a conta para editar:",
                lambda acc: f"{acc.nome} - {acc.banco} ({self.format_currency(acc.saldo_atual)})",
                lambda acc: acc.id
            )
            
            if not account:
                return
            
            self.print(f"\n[cyan]Editando conta: {account.nome}[/cyan]")
            self.print("[dim]Deixe em branco para manter o valor atual[/dim]\n")
            
            # Get new values
            nome = self.get_text_input(f"Nome [{account.nome}]") or account.nome
            banco = self.get_text_input(f"Banco [{account.banco}]") or account.banco
            agencia = self.get_text_input(f"Agência [{account.agencia}]") or account.agencia
            conta_num = self.get_text_input(f"Conta [{account.conta}]") or account.conta
            
            # Type selection
            if self.get_confirmation("Alterar tipo da conta?", default=False):
                tipo = self.get_enum_choice("Novo tipo:", TipoConta, lambda t: t.value.title())
            else:
                tipo = account.tipo
            
            # Shared status
            if self.get_confirmation("Alterar status compartilhado?", default=False):
                compartilhado = self.get_confirmation("Compartilhada com Alzi?", account.compartilhado_com_alzi)
            else:
                compartilhado = account.compartilhado_com_alzi
            
            # Active status
            if self.get_confirmation("Alterar status ativo?", default=False):
                ativa = self.get_confirmation("Conta ativa?", account.ativa)
            else:
                ativa = account.ativa
            
            # Update account
            success = self.account_service.update_account(
                account.id,
                nome=nome,
                banco=banco,
                agencia=agencia,
                conta=conta_num,
                tipo=tipo,
                compartilhado_com_alzi=compartilhado,
                ativa=ativa
            )
            
            if success:
                self.show_success("Conta atualizada com sucesso!")
            else:
                self.show_error("Falha ao atualizar conta")
            
        except Exception as e:
            self.handle_exception(e, "edição de conta")
        
        self.wait_for_enter()
    
    def delete_account(self):
        """Delete an account"""
        self.clear()
        header = self.create_header_panel("🗑️ Excluir Conta")
        self.print(header)
        
        try:
            accounts = self.account_service.list_accounts()
            
            if not accounts:
                self.show_info("Nenhuma conta disponível para exclusão")
                self.wait_for_enter()
                return
            
            # Select account
            account = self.select_from_list(
                accounts,
                "Selecione a conta para excluir:",
                lambda acc: f"{acc.nome} - {acc.banco} ({self.format_currency(acc.saldo_atual)})",
                lambda acc: acc.id
            )
            
            if not account:
                return
            
            # Confirmation
            self.show_warning(f"Conta selecionada: {account.nome} - {account.banco}")
            self.show_warning("Esta ação não pode ser desfeita!")
            
            if not self.get_confirmation("Confirma a exclusão da conta?", default=False):
                self.show_info("Exclusão cancelada")
                self.wait_for_enter()
                return
            
            # Delete account
            success = self.account_service.delete_account(account.id)
            
            if success:
                self.show_success("Conta excluída com sucesso!")
            else:
                self.show_error("Falha ao excluir conta")
            
        except Exception as e:
            self.handle_exception(e, "exclusão de conta")
        
        self.wait_for_enter()
    
    def show_account_details(self):
        """Show detailed account information"""
        self.clear()
        header = self.create_header_panel("🔍 Detalhes da Conta")
        self.print(header)
        
        try:
            accounts = self.account_service.list_accounts()
            
            if not accounts:
                self.show_info("Nenhuma conta disponível")
                self.wait_for_enter()
                return
            
            # Select account
            account = self.select_from_list(
                accounts,
                "Selecione a conta para ver detalhes:",
                lambda acc: f"{acc.nome} - {acc.banco}",
                lambda acc: acc.id
            )
            
            if not account:
                return
            
            # Display details
            self.print_newline()
            details_panel = self.create_info_panel(
                f"[bold]ID:[/bold] {account.id}\n"
                f"[bold]Nome:[/bold] {account.nome}\n"
                f"[bold]Banco:[/bold] {account.banco}\n"
                f"[bold]Agência:[/bold] {account.agencia}\n"
                f"[bold]Conta:[/bold] {account.conta}\n"
                f"[bold]Tipo:[/bold] {account.tipo.value.title()}\n"
                f"[bold]Saldo Inicial:[/bold] {self.format_currency(account.saldo_inicial)}\n"
                f"[bold]Saldo Atual:[/bold] {self.format_currency(account.saldo_atual)}\n"
                f"[bold]Compartilhada com Alzi:[/bold] {'Sim' if account.compartilhado_com_alzi else 'Não'}\n"
                f"[bold]Status:[/bold] {'Ativa' if account.ativa else 'Inativa'}\n"
                f"[bold]Criada em:[/bold] {self.format_date(account.created_at) if account.created_at else 'N/A'}\n"
                f"[bold]Atualizada em:[/bold] {self.format_date(account.updated_at) if account.updated_at else 'N/A'}",
                title=f"Detalhes - {account.nome}"
            )
            self.print(details_panel)
            
        except Exception as e:
            self.handle_exception(e, "exibição de detalhes")
        
        self.wait_for_enter()