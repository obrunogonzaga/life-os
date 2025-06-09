"""
Credit Card Management UI for Finance Module

This module provides the user interface for managing credit cards,
including creation, listing, editing, and deletion of cards.
"""

from typing import List, Optional
from .base_ui import BaseUI
from ..services.card_service import CardService
from ..services.account_service import AccountService
from utils.finance_models import CartaoCredito, BandeiraCartao


class CardUI(BaseUI):
    """User interface for credit card management"""
    
    def __init__(self, card_service: CardService, account_service: AccountService):
        super().__init__()
        self.card_service = card_service
        self.account_service = account_service
        self.menu_options = [
            ("1", "➕ Criar Novo Cartão"),
            ("2", "📋 Listar Cartões"),
            ("3", "✏️ Editar Cartão"),
            ("4", "🗑️ Excluir Cartão"),
            ("5", "🔍 Detalhes do Cartão"),
            ("6", "📊 Resumo de Limites"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
    
    def show_menu(self):
        """Display the card management menu"""
        from .main_menu_ui import MainMenuUI
        main_ui = MainMenuUI()
        
        action_handlers = {
            "1": self.create_card,
            "2": self.list_cards,
            "3": self.edit_card,
            "4": self.delete_card,
            "5": self.show_card_details,
            "6": self.show_limits_summary
        }
        
        main_ui.run_submenu_loop(
            "💳 Gerenciamento de Cartões",
            self.menu_options,
            action_handlers
        )
    
    def create_card(self):
        """Create a new credit card"""
        self.clear()
        header = self.create_header_panel("➕ Criar Novo Cartão")
        self.print(header)
        
        try:
            # Get card details
            nome = self.get_text_input("Nome do cartão")
            if not nome:
                self.show_error("Nome do cartão é obrigatório")
                self.wait_for_enter()
                return
            
            banco = self.get_text_input("Nome do banco")
            if not banco:
                self.show_error("Nome do banco é obrigatório")
                self.wait_for_enter()
                return
            
            # Card brand selection
            bandeira = self.get_enum_choice(
                "Bandeira do cartão:",
                BandeiraCartao,
                lambda b: b.value.replace('_', ' ').title()
            )
            
            limite = self.get_float_input("Limite do cartão", min_value=0.1)
            
            dia_vencimento = self.get_int_input("Dia do vencimento (1-31)", min_value=1, max_value=31)
            dia_fechamento = self.get_int_input("Dia do fechamento (1-31)", min_value=1, max_value=31)
            
            # Validate dates
            if dia_vencimento == dia_fechamento:
                self.show_error("Dia de vencimento e fechamento não podem ser iguais")
                self.wait_for_enter()
                return
            
            # Optional account linking
            conta_vinculada_id = None
            if self.get_confirmation("Vincular a uma conta corrente?", default=False):
                accounts = self.account_service.list_accounts(active_only=True)
                if accounts:
                    account = self.select_from_list(
                        accounts,
                        "Selecione a conta para vincular:",
                        lambda acc: f"{acc.nome} - {acc.banco}",
                        lambda acc: acc.id,
                        allow_none=True
                    )
                    if account:
                        conta_vinculada_id = account.id
                else:
                    self.show_warning("Nenhuma conta disponível para vinculação")
            
            compartilhado = self.get_confirmation("Cartão compartilhado com Alzi?", default=False)
            
            # Create card
            card = self.card_service.create_card(
                nome=nome,
                banco=banco,
                bandeira=bandeira,
                limite=limite,
                dia_vencimento=dia_vencimento,
                dia_fechamento=dia_fechamento,
                conta_vinculada_id=conta_vinculada_id,
                compartilhado_com_alzi=compartilhado
            )
            
            if card:
                self.show_success(f"Cartão '{nome}' criado com sucesso!")
                self.show_info(f"ID: {self.format_id(card.id)}")
                self.show_info(f"Limite disponível: {self.format_currency(card.limite_disponivel)}")
            else:
                self.show_error("Falha ao criar cartão")
            
        except Exception as e:
            self.handle_exception(e, "criação de cartão")
        
        self.wait_for_enter()
    
    def list_cards(self):
        """List all credit cards"""
        self.clear()
        header = self.create_header_panel("📋 Lista de Cartões")
        self.print(header)
        
        try:
            cards = self.card_service.list_cards()
            
            if not cards:
                self.show_info("Nenhum cartão cadastrado")
                self.wait_for_enter()
                return
            
            # Create table
            columns = [
                ("ID", "cyan", 10),
                ("Nome", "white", 20),
                ("Banco", "yellow", 15),
                ("Bandeira", "magenta", 12),
                ("Limite", "green", 12),
                ("Disponível", "blue", 12),
                ("Uso", "red", 8),
                ("Venc.", "white", 6),
                ("Fech.", "white", 6),
                ("Alzi", "red", 6),
                ("Status", "green", 8)
            ]
            
            data = []
            for card in cards:
                uso_percentage = ((card.limite - card.limite_disponivel) / card.limite * 100) if card.limite > 0 else 0
                data.append([
                    self.format_id(card.id),
                    card.nome,
                    card.banco,
                    card.bandeira.value.replace('_', ' ').title(),
                    self.format_currency(card.limite),
                    self.format_currency(card.limite_disponivel),
                    self.format_percentage(uso_percentage),
                    str(card.dia_vencimento),
                    str(card.dia_fechamento),
                    self.format_status_icon(card.compartilhado_com_alzi),
                    self.format_status_icon(card.ativo)
                ])
            
            table = self.create_data_table(columns, data, "Cartões Cadastrados")
            self.print(table)
            
            # Summary
            active_cards = [card for card in cards if card.ativo]
            total_limit = sum(card.limite for card in active_cards)
            total_available = sum(card.limite_disponivel for card in active_cards)
            total_used = total_limit - total_available
            shared_cards = sum(1 for card in active_cards if card.compartilhado_com_alzi)
            
            self.print_newline()
            self.show_info(f"Total de cartões: {len(cards)}")
            self.show_info(f"Cartões ativos: {len(active_cards)}")
            self.show_info(f"Cartões compartilhados: {shared_cards}")
            self.show_info(f"Limite total: {self.format_currency(total_limit)}")
            self.show_info(f"Limite disponível: {self.format_currency(total_available)}")
            self.show_info(f"Limite usado: {self.format_currency(total_used)} ({self.format_percentage(total_used/total_limit*100 if total_limit > 0 else 0)})")
            
        except Exception as e:
            self.handle_exception(e, "listagem de cartões")
        
        self.wait_for_enter()
    
    def edit_card(self):
        """Edit an existing credit card"""
        self.clear()
        header = self.create_header_panel("✏️ Editar Cartão")
        self.print(header)
        
        try:
            cards = self.card_service.list_cards()
            
            if not cards:
                self.show_info("Nenhum cartão disponível para edição")
                self.wait_for_enter()
                return
            
            # Select card
            card = self.select_from_list(
                cards,
                "Selecione o cartão para editar:",
                lambda c: f"{c.nome} - {c.banco} ({self.format_currency(c.limite)})",
                lambda c: c.id
            )
            
            if not card:
                return
            
            self.print(f"\n[cyan]Editando cartão: {card.nome}[/cyan]")
            self.print("[dim]Deixe em branco para manter o valor atual[/dim]\n")
            
            # Get new values
            nome = self.get_text_input(f"Nome [{card.nome}]") or card.nome
            banco = self.get_text_input(f"Banco [{card.banco}]") or card.banco
            
            # Bandeira selection
            if self.get_confirmation("Alterar bandeira?", default=False):
                bandeira = self.get_enum_choice("Nova bandeira:", BandeiraCartao, 
                                              lambda b: b.value.replace('_', ' ').title())
            else:
                bandeira = card.bandeira
            
            # Limite
            if self.get_confirmation("Alterar limite?", default=False):
                limite = self.get_float_input(f"Novo limite", default=card.limite, min_value=0.1)
            else:
                limite = card.limite
            
            # Datas
            if self.get_confirmation("Alterar datas?", default=False):
                dia_vencimento = self.get_int_input(f"Dia vencimento [{card.dia_vencimento}]", 
                                                  default=card.dia_vencimento, min_value=1, max_value=31)
                dia_fechamento = self.get_int_input(f"Dia fechamento [{card.dia_fechamento}]", 
                                                  default=card.dia_fechamento, min_value=1, max_value=31)
                
                if dia_vencimento == dia_fechamento:
                    self.show_error("Dia de vencimento e fechamento não podem ser iguais")
                    self.wait_for_enter()
                    return
            else:
                dia_vencimento = card.dia_vencimento
                dia_fechamento = card.dia_fechamento
            
            # Shared status
            if self.get_confirmation("Alterar status compartilhado?", default=False):
                compartilhado = self.get_confirmation("Compartilhado com Alzi?", card.compartilhado_com_alzi)
            else:
                compartilhado = card.compartilhado_com_alzi
            
            # Active status
            if self.get_confirmation("Alterar status ativo?", default=False):
                ativo = self.get_confirmation("Cartão ativo?", card.ativo)
            else:
                ativo = card.ativo
            
            # Update card
            success = self.card_service.update_card(
                card.id,
                nome=nome,
                banco=banco,
                bandeira=bandeira,
                limite=limite,
                dia_vencimento=dia_vencimento,
                dia_fechamento=dia_fechamento,
                compartilhado_com_alzi=compartilhado,
                ativo=ativo
            )
            
            if success:
                self.show_success("Cartão atualizado com sucesso!")
            else:
                self.show_error("Falha ao atualizar cartão")
            
        except Exception as e:
            self.handle_exception(e, "edição de cartão")
        
        self.wait_for_enter()
    
    def delete_card(self):
        """Delete a credit card"""
        self.clear()
        header = self.create_header_panel("🗑️ Excluir Cartão")
        self.print(header)
        
        try:
            cards = self.card_service.list_cards()
            
            if not cards:
                self.show_info("Nenhum cartão disponível para exclusão")
                self.wait_for_enter()
                return
            
            # Select card
            card = self.select_from_list(
                cards,
                "Selecione o cartão para desativar:",
                lambda c: f"{c.nome} - {c.banco} ({self.format_currency(c.limite)})",
                lambda c: c.id
            )
            
            if not card:
                return
            
            # Confirmation
            self.show_warning(f"Cartão selecionado: {card.nome} - {card.banco}")
            self.show_warning("O cartão será desativado (não excluído)")
            
            if not self.get_confirmation("Confirma a desativação do cartão?", default=False):
                self.show_info("Desativação cancelada")
                self.wait_for_enter()
                return
            
            # Deactivate card
            success = self.card_service.deactivate_card(card.id)
            
            if success:
                self.show_success("Cartão desativado com sucesso!")
            else:
                self.show_error("Falha ao desativar cartão")
            
        except Exception as e:
            self.handle_exception(e, "desativação de cartão")
        
        self.wait_for_enter()
    
    def show_card_details(self):
        """Show detailed card information"""
        self.clear()
        header = self.create_header_panel("🔍 Detalhes do Cartão")
        self.print(header)
        
        try:
            cards = self.card_service.list_cards()
            
            if not cards:
                self.show_info("Nenhum cartão disponível")
                self.wait_for_enter()
                return
            
            # Select card
            card = self.select_from_list(
                cards,
                "Selecione o cartão para ver detalhes:",
                lambda c: f"{c.nome} - {c.banco}",
                lambda c: c.id
            )
            
            if not card:
                return
            
            # Get linked account name
            conta_vinculada = "Não vinculada"
            if card.conta_vinculada_id:
                account = self.account_service.get_account_by_id(card.conta_vinculada_id)
                if account:
                    conta_vinculada = f"{account.nome} - {account.banco}"
            
            # Calculate usage
            usado = card.limite - card.limite_disponivel
            percentual_uso = (usado / card.limite * 100) if card.limite > 0 else 0
            
            # Display details
            self.print_newline()
            details_panel = self.create_info_panel(
                f"[bold]ID:[/bold] {card.id}\n"
                f"[bold]Nome:[/bold] {card.nome}\n"
                f"[bold]Banco:[/bold] {card.banco}\n"
                f"[bold]Bandeira:[/bold] {card.bandeira.value.replace('_', ' ').title()}\n"
                f"[bold]Limite Total:[/bold] {self.format_currency(card.limite)}\n"
                f"[bold]Limite Disponível:[/bold] {self.format_currency(card.limite_disponivel)}\n"
                f"[bold]Limite Usado:[/bold] {self.format_currency(usado)} ({self.format_percentage(percentual_uso)})\n"
                f"[bold]Dia Vencimento:[/bold] {card.dia_vencimento}\n"
                f"[bold]Dia Fechamento:[/bold] {card.dia_fechamento}\n"
                f"[bold]Conta Vinculada:[/bold] {conta_vinculada}\n"
                f"[bold]Compartilhado com Alzi:[/bold] {'Sim' if card.compartilhado_com_alzi else 'Não'}\n"
                f"[bold]Status:[/bold] {'Ativo' if card.ativo else 'Inativo'}\n"
                f"[bold]Criado em:[/bold] {self.format_date(card.created_at) if card.created_at else 'N/A'}\n"
                f"[bold]Atualizado em:[/bold] {self.format_date(card.updated_at) if card.updated_at else 'N/A'}",
                title=f"Detalhes - {card.nome}"
            )
            self.print(details_panel)
            
        except Exception as e:
            self.handle_exception(e, "exibição de detalhes")
        
        self.wait_for_enter()
    
    def show_limits_summary(self):
        """Show summary of credit limits"""
        self.clear()
        header = self.create_header_panel("📊 Resumo de Limites")
        self.print(header)
        
        try:
            limits_summary = self.card_service.get_total_limit()
            
            # Display summary
            summary_panel = self.create_info_panel(
                f"[bold]Limite Total:[/bold] {self.format_currency(limits_summary['total_limit'])}\n"
                f"[bold]Limite Disponível:[/bold] {self.format_currency(limits_summary['available_limit'])}\n"
                f"[bold]Limite Usado:[/bold] {self.format_currency(limits_summary['used_limit'])}\n"
                f"[bold]Percentual Usado:[/bold] {self.format_percentage(limits_summary['used_limit']/limits_summary['total_limit']*100 if limits_summary['total_limit'] > 0 else 0)}",
                title="Resumo Geral de Limites"
            )
            self.print(summary_panel)
            
            # Cards by due date
            cards_by_due = self.card_service.get_cards_by_due_date()
            
            if cards_by_due:
                self.print_newline()
                self.print("[bold cyan]📅 Cartões por Data de Vencimento[/bold cyan]")
                
                for dia, cards in sorted(cards_by_due.items()):
                    self.print(f"\n[yellow]Dia {dia}:[/yellow]")
                    for card in cards:
                        usage = ((card.limite - card.limite_disponivel) / card.limite * 100) if card.limite > 0 else 0
                        self.print(f"  • {card.nome} - {self.format_currency(card.limite)} ({self.format_percentage(usage)} usado)")
            
        except Exception as e:
            self.handle_exception(e, "resumo de limites")
        
        self.wait_for_enter()