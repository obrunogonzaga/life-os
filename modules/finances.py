from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

from utils.finance_client import FinanceClient
from utils.finance_models import (
    ContaCorrente, CartaoCredito, Transacao, TipoTransacao, 
    TipoConta, BandeiraCartao, StatusTransacao
)

class FinancesModule:
    def __init__(self):
        self.console = Console()
        self.client = FinanceClient()

    def run(self):
        """Executa o módulo de finanças"""
        while True:
            try:
                self._show_main_menu()
                opcao = Prompt.ask("Escolha uma opção", choices=[
                    "1", "2", "3", "4", "5", "6", "7", "8", "9", "M", "m"
                ])
                
                if opcao.upper() == "M":
                    break
                
                opcoes = {
                    "1": self._dashboard,
                    "2": self._menu_contas,
                    "3": self._menu_cartoes,
                    "4": self._menu_transacoes,
                    "5": self._transacoes_compartilhadas_alzi,
                    "6": self._relatorios,
                    "7": self._configuracoes,
                    "8": self._importar_exportar,
                    "9": self._estatisticas
                }
                
                if opcao in opcoes:
                    opcoes[opcao]()
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Saindo do módulo de finanças...[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Erro: {e}[/red]")

    def _show_main_menu(self):
        """Exibe o menu principal do módulo de finanças"""
        self.console.clear()
        
        # Header
        header = Panel(
            Align.center("[bold cyan]💰 MÓDULO DE FINANÇAS[/bold cyan]\n[dim]Gestão Financeira Pessoal[/dim]"),
            style="cyan"
        )
        self.console.print(header)
        
        # Menu options
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Opção", style="bold yellow", width=4)
        menu_table.add_column("Descrição", style="white")
        
        menu_items = [
            ("1", "📊 Dashboard Financeiro"),
            ("2", "🏦 Gerenciar Contas Correntes"),
            ("3", "💳 Gerenciar Cartões de Crédito"),
            ("4", "📝 Gerenciar Transações"),
            ("5", "👫 Transações Compartilhadas com Alzi"),
            ("6", "📈 Relatórios e Análises"),
            ("7", "⚙️ Configurações"),
            ("8", "📤 Importar/Exportar Dados"),
            ("9", "📊 Estatísticas Avançadas"),
            ("M", "🔙 Voltar ao Menu Principal")
        ]
        
        for opcao, descricao in menu_items:
            menu_table.add_row(opcao, descricao)
        
        self.console.print(menu_table)
        self.console.print()

    def _dashboard(self):
        """Exibe o dashboard financeiro"""
        self.console.clear()
        self.console.print(Panel("[bold cyan]📊 Dashboard Financeiro[/bold cyan]", style="cyan"))
        
        try:
            resumo = self.client.obter_resumo_financeiro()
            
            # Layout principal
            layout = Layout()
            layout.split_column(
                Layout(name="resumo", size=8),
                Layout(name="detalhes")
            )
            
            # Resumo geral
            resumo_table = Table(title="Resumo Geral", show_header=True, header_style="bold magenta")
            resumo_table.add_column("Categoria", style="cyan")
            resumo_table.add_column("Valor", style="green", justify="right")
            
            resumo_table.add_row("💰 Saldo Total em Contas", f"R$ {resumo.saldo_total_contas:,.2f}")
            resumo_table.add_row("💳 Limite Total Cartões", f"R$ {resumo.limite_total_cartoes:,.2f}")
            resumo_table.add_row("💸 Limite Disponível", f"R$ {resumo.limite_disponivel_cartoes:,.2f}")
            resumo_table.add_row("📉 Gastos Este Mês", f"R$ {resumo.valor_total_gastos_mes:,.2f}")
            resumo_table.add_row("👫 Compartilhado Alzi", f"R$ {resumo.valor_compartilhado_alzi_mes:,.2f}")
            
            layout["resumo"].update(Panel(resumo_table, border_style="blue"))
            
            # Detalhes das contas e cartões
            detalhes_layout = Layout()
            detalhes_layout.split_row(
                Layout(name="contas"),
                Layout(name="cartoes")
            )
            
            # Contas
            contas = self.client.listar_contas()
            contas_table = Table(title=f"Contas ({len(contas)})", show_header=True, header_style="bold green")
            contas_table.add_column("Nome", style="cyan")
            contas_table.add_column("Banco", style="white")
            contas_table.add_column("Saldo", style="green", justify="right")
            contas_table.add_column("Alzi", style="yellow", justify="center")
            
            for conta in contas[:5]:  # Mostrar apenas as primeiras 5
                alzi_icon = "✓" if conta.compartilhado_com_alzi else "✗"
                contas_table.add_row(
                    conta.nome,
                    conta.banco,
                    f"R$ {conta.saldo_atual:,.2f}",
                    alzi_icon
                )
            
            detalhes_layout["contas"].update(Panel(contas_table, border_style="green"))
            
            # Cartões
            cartoes = self.client.listar_cartoes()
            cartoes_table = Table(title=f"Cartões ({len(cartoes)})", show_header=True, header_style="bold red")
            cartoes_table.add_column("Nome", style="cyan")
            cartoes_table.add_column("Banco", style="white")
            cartoes_table.add_column("Disponível", style="green", justify="right")
            cartoes_table.add_column("Alzi", style="yellow", justify="center")
            
            for cartao in cartoes[:5]:  # Mostrar apenas os primeiros 5
                alzi_icon = "✓" if cartao.compartilhado_com_alzi else "✗"
                cartoes_table.add_row(
                    cartao.nome,
                    cartao.banco,
                    f"R$ {cartao.limite_disponivel:,.2f}",
                    alzi_icon
                )
            
            detalhes_layout["cartoes"].update(Panel(cartoes_table, border_style="red"))
            
            layout["detalhes"].update(detalhes_layout)
            
            self.console.print(layout)
            
        except Exception as e:
            self.console.print(f"[red]Erro ao carregar dashboard: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _menu_contas(self):
        """Menu de gerenciamento de contas correntes"""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold green]🏦 Gerenciar Contas Correntes[/bold green]", style="green"))
            
            self.console.print("1. ➕ Criar Nova Conta")
            self.console.print("2. 📋 Listar Contas")
            self.console.print("3. ✏️ Editar Conta")
            self.console.print("4. 🗑️ Excluir Conta")
            self.console.print("5. 📊 Detalhes da Conta")
            self.console.print("M. 🔙 Voltar")
            
            opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "4", "5", "M", "m"])
            
            if opcao.upper() == "M":
                break
            elif opcao == "1":
                self._criar_conta()
            elif opcao == "2":
                self._listar_contas()
            elif opcao == "3":
                self._editar_conta()
            elif opcao == "4":
                self._excluir_conta()
            elif opcao == "5":
                self._detalhes_conta()

    def _criar_conta(self):
        """Cria uma nova conta corrente"""
        self.console.print(Panel("[bold green]➕ Criar Nova Conta[/bold green]", style="green"))
        
        try:
            nome = Prompt.ask("Nome da conta")
            banco = Prompt.ask("Nome do banco")
            agencia = Prompt.ask("Agência")
            conta = Prompt.ask("Número da conta")
            
            # Tipo de conta
            tipos_disponiveis = {
                "1": TipoConta.CORRENTE,
                "2": TipoConta.POUPANCA,
                "3": TipoConta.INVESTIMENTO
            }
            
            self.console.print("\nTipos de conta disponíveis:")
            self.console.print("1. Conta Corrente")
            self.console.print("2. Poupança")
            self.console.print("3. Investimento")
            
            tipo_opcao = Prompt.ask("Tipo da conta", choices=["1", "2", "3"])
            tipo = tipos_disponiveis[tipo_opcao]
            
            saldo_inicial = FloatPrompt.ask("Saldo inicial", default=0.0)
            compartilhado_com_alzi = Confirm.ask("Compartilhado com Alzi?", default=False)
            
            conta_criada = self.client.criar_conta(
                nome=nome,
                banco=banco,
                agencia=agencia,
                conta=conta,
                tipo=tipo,
                saldo_inicial=saldo_inicial,
                compartilhado_com_alzi=compartilhado_com_alzi
            )
            
            if conta_criada:
                self.console.print(f"[green]✓ Conta '{nome}' criada com sucesso![/green]")
            else:
                self.console.print("[red]✗ Erro ao criar conta[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _listar_contas(self):
        """Lista todas as contas correntes"""
        self.console.print(Panel("[bold green]📋 Lista de Contas[/bold green]", style="green"))
        
        try:
            contas = self.client.listar_contas()
            
            if not contas:
                self.console.print("[yellow]Nenhuma conta cadastrada.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold green")
                table.add_column("ID", style="dim", width=8)
                table.add_column("Nome", style="cyan")
                table.add_column("Banco", style="white")
                table.add_column("Agência", style="white")
                table.add_column("Conta", style="white")
                table.add_column("Tipo", style="blue")
                table.add_column("Saldo", style="green", justify="right")
                table.add_column("Alzi", style="yellow", justify="center")
                table.add_column("Status", style="magenta", justify="center")
                
                for conta in contas:
                    alzi_icon = "✓" if conta.compartilhado_com_alzi else "✗"
                    status_icon = "🟢" if conta.ativa else "🔴"
                    
                    table.add_row(
                        conta.id[:8],
                        conta.nome,
                        conta.banco,
                        conta.agencia,
                        conta.conta,
                        conta.tipo.value.title(),
                        f"R$ {conta.saldo_atual:,.2f}",
                        alzi_icon,
                        status_icon
                    )
                
                self.console.print(table)
                
        except Exception as e:
            self.console.print(f"[red]Erro ao listar contas: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _editar_conta(self):
        """Edita uma conta existente"""
        self.console.print(Panel("[bold yellow]✏️ Editar Conta[/bold yellow]", style="yellow"))
        
        try:
            contas = self.client.listar_contas()
            if not contas:
                self.console.print("[yellow]Nenhuma conta cadastrada.[/yellow]")
                return
            
            # Mostrar contas para seleção
            for i, conta in enumerate(contas, 1):
                self.console.print(f"{i}. {conta.nome} - {conta.banco} (R$ {conta.saldo_atual:,.2f})")
            
            indice = IntPrompt.ask("Número da conta para editar", default=1) - 1
            
            if 0 <= indice < len(contas):
                conta = contas[indice]
                
                self.console.print(f"\nEditando conta: [cyan]{conta.nome}[/cyan]")
                self.console.print("[dim]Deixe em branco para manter o valor atual[/dim]")
                
                nome = Prompt.ask("Nome", default=conta.nome)
                banco = Prompt.ask("Banco", default=conta.banco)
                compartilhado = Confirm.ask("Compartilhado com Alzi", default=conta.compartilhado_com_alzi)
                
                sucesso = self.client.atualizar_conta(
                    conta.id,
                    nome=nome,
                    banco=banco,
                    compartilhado_com_alzi=compartilhado
                )
                
                if sucesso:
                    self.console.print(f"[green]✓ Conta '{nome}' atualizada com sucesso![/green]")
                else:
                    self.console.print("[red]✗ Erro ao atualizar conta[/red]")
            else:
                self.console.print("[red]Conta inválida.[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _excluir_conta(self):
        """Exclui (desativa) uma conta"""
        self.console.print(Panel("[bold red]🗑️ Excluir Conta[/bold red]", style="red"))
        
        try:
            contas = self.client.listar_contas()
            if not contas:
                self.console.print("[yellow]Nenhuma conta cadastrada.[/yellow]")
                return
            
            # Mostrar contas para seleção
            for i, conta in enumerate(contas, 1):
                self.console.print(f"{i}. {conta.nome} - {conta.banco}")
            
            indice = IntPrompt.ask("Número da conta para excluir", default=1) - 1
            
            if 0 <= indice < len(contas):
                conta = contas[indice]
                
                if Confirm.ask(f"Tem certeza que deseja excluir a conta '{conta.nome}'?"):
                    sucesso = self.client.excluir_conta(conta.id)
                    
                    if sucesso:
                        self.console.print(f"[green]✓ Conta '{conta.nome}' excluída com sucesso![/green]")
                    else:
                        self.console.print("[red]✗ Erro ao excluir conta[/red]")
                else:
                    self.console.print("[yellow]Operação cancelada.[/yellow]")
            else:
                self.console.print("[red]Conta inválida.[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _detalhes_conta(self):
        """Mostra detalhes de uma conta específica"""
        # Implementação será adicionada posteriormente
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _menu_cartoes(self):
        """Menu de gerenciamento de cartões de crédito"""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold red]💳 Gerenciar Cartões de Crédito[/bold red]", style="red"))
            
            self.console.print("1. ➕ Criar Novo Cartão")
            self.console.print("2. 📋 Listar Cartões")
            self.console.print("3. ✏️ Editar Cartão")
            self.console.print("4. 🗑️ Excluir Cartão")
            self.console.print("5. 📊 Detalhes do Cartão")
            self.console.print("M. 🔙 Voltar")
            
            opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "4", "5", "M", "m"])
            
            if opcao.upper() == "M":
                break
            elif opcao == "1":
                self._criar_cartao()
            elif opcao == "2":
                self._listar_cartoes()
            elif opcao == "3":
                self._editar_cartao()
            elif opcao == "4":
                self._excluir_cartao()
            elif opcao == "5":
                self._detalhes_cartao()

    def _criar_cartao(self):
        """Cria um novo cartão de crédito"""
        self.console.print(Panel("[bold red]➕ Criar Novo Cartão[/bold red]", style="red"))
        
        try:
            nome = Prompt.ask("Nome do cartão")
            banco = Prompt.ask("Nome do banco")
            
            # Bandeira do cartão
            bandeiras_disponiveis = {
                "1": BandeiraCartao.VISA,
                "2": BandeiraCartao.MASTERCARD,
                "3": BandeiraCartao.ELO,
                "4": BandeiraCartao.AMERICAN_EXPRESS,
                "5": BandeiraCartao.HIPERCARD
            }
            
            self.console.print("\nBandeiras disponíveis:")
            self.console.print("1. Visa")
            self.console.print("2. Mastercard")
            self.console.print("3. Elo")
            self.console.print("4. American Express")
            self.console.print("5. Hipercard")
            
            bandeira_opcao = Prompt.ask("Bandeira do cartão", choices=["1", "2", "3", "4", "5"])
            bandeira = bandeiras_disponiveis[bandeira_opcao]
            
            limite = FloatPrompt.ask("Limite do cartão")
            dia_vencimento = IntPrompt.ask("Dia do vencimento (1-31)", default=10)
            dia_fechamento = IntPrompt.ask("Dia do fechamento (1-31)", default=5)
            
            # Conta vinculada (opcional)
            contas = self.client.listar_contas()
            conta_vinculada_id = None
            
            if contas and Confirm.ask("Vincular a uma conta corrente?"):
                self.console.print("\nContas disponíveis:")
                for i, conta in enumerate(contas, 1):
                    self.console.print(f"{i}. {conta.nome} - {conta.banco}")
                
                indice_conta = IntPrompt.ask("Número da conta", default=1) - 1
                if 0 <= indice_conta < len(contas):
                    conta_vinculada_id = contas[indice_conta].id
            
            compartilhado_com_alzi = Confirm.ask("Compartilhado com Alzi?", default=False)
            
            cartao_criado = self.client.criar_cartao(
                nome=nome,
                banco=banco,
                bandeira=bandeira,
                limite=limite,
                dia_vencimento=dia_vencimento,
                dia_fechamento=dia_fechamento,
                conta_vinculada_id=conta_vinculada_id,
                compartilhado_com_alzi=compartilhado_com_alzi
            )
            
            if cartao_criado:
                self.console.print(f"[green]✓ Cartão '{nome}' criado com sucesso![/green]")
            else:
                self.console.print("[red]✗ Erro ao criar cartão[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _listar_cartoes(self):
        """Lista todos os cartões de crédito"""
        self.console.print(Panel("[bold red]📋 Lista de Cartões[/bold red]", style="red"))
        
        try:
            cartoes = self.client.listar_cartoes()
            
            if not cartoes:
                self.console.print("[yellow]Nenhum cartão cadastrado.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold red")
                table.add_column("ID", style="dim", width=8)
                table.add_column("Nome", style="cyan")
                table.add_column("Banco", style="white")
                table.add_column("Bandeira", style="blue")
                table.add_column("Limite", style="green", justify="right")
                table.add_column("Disponível", style="green", justify="right")
                table.add_column("Venc.", style="yellow", justify="center")
                table.add_column("Alzi", style="yellow", justify="center")
                table.add_column("Status", style="magenta", justify="center")
                
                for cartao in cartoes:
                    alzi_icon = "✓" if cartao.compartilhado_com_alzi else "✗"
                    status_icon = "🟢" if cartao.ativo else "🔴"
                    
                    table.add_row(
                        cartao.id[:8],
                        cartao.nome,
                        cartao.banco,
                        cartao.bandeira.value.title(),
                        f"R$ {cartao.limite:,.2f}",
                        f"R$ {cartao.limite_disponivel:,.2f}",
                        str(cartao.dia_vencimento),
                        alzi_icon,
                        status_icon
                    )
                
                self.console.print(table)
                
        except Exception as e:
            self.console.print(f"[red]Erro ao listar cartões: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _editar_cartao(self):
        """Edita um cartão existente"""
        # Implementação similar à edição de conta
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _excluir_cartao(self):
        """Exclui (desativa) um cartão"""
        # Implementação similar à exclusão de conta
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _detalhes_cartao(self):
        """Mostra detalhes de um cartão específico"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _menu_transacoes(self):
        """Menu de gerenciamento de transações"""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold blue]📝 Gerenciar Transações[/bold blue]", style="blue"))
            
            self.console.print("1. ➕ Nova Transação")
            self.console.print("2. 📋 Listar Transações")
            self.console.print("3. 🔍 Buscar Transações")
            self.console.print("4. ✏️ Editar Transação")
            self.console.print("5. 🗑️ Excluir Transação")
            self.console.print("6. 📊 Transações por Categoria")
            self.console.print("M. 🔙 Voltar")
            
            opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "4", "5", "6", "M", "m"])
            
            if opcao.upper() == "M":
                break
            elif opcao == "1":
                self._criar_transacao()
            elif opcao == "2":
                self._listar_transacoes()
            elif opcao == "3":
                self._buscar_transacoes()
            elif opcao == "4":
                self._editar_transacao()
            elif opcao == "5":
                self._excluir_transacao()
            elif opcao == "6":
                self._transacoes_por_categoria()

    def _criar_transacao(self):
        """Cria uma nova transação"""
        self.console.print(Panel("[bold blue]➕ Nova Transação[/bold blue]", style="blue"))
        
        try:
            descricao = Prompt.ask("Descrição da transação")
            valor = FloatPrompt.ask("Valor")
            
            # Tipo de transação
            self.console.print("\nTipo de transação:")
            self.console.print("1. Débito (saída)")
            self.console.print("2. Crédito (entrada)")
            
            tipo_opcao = Prompt.ask("Tipo", choices=["1", "2"])
            tipo = TipoTransacao.DEBITO if tipo_opcao == "1" else TipoTransacao.CREDITO
            
            # Data da transação
            data_transacao = Prompt.ask("Data da transação (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))
            
            categoria = Prompt.ask("Categoria", default="")
            observacoes = Prompt.ask("Observações", default="")
            
            # Conta ou cartão
            self.console.print("\nOrigens disponíveis:")
            self.console.print("1. Conta corrente")
            self.console.print("2. Cartão de crédito")
            
            origem_opcao = Prompt.ask("Origem", choices=["1", "2"])
            
            conta_id = None
            cartao_id = None
            
            if origem_opcao == "1":
                contas = self.client.listar_contas()
                if contas:
                    for i, conta in enumerate(contas, 1):
                        self.console.print(f"{i}. {conta.nome} - {conta.banco}")
                    
                    indice_conta = IntPrompt.ask("Número da conta", default=1) - 1
                    if 0 <= indice_conta < len(contas):
                        conta_id = contas[indice_conta].id
            else:
                cartoes = self.client.listar_cartoes()
                if cartoes:
                    for i, cartao in enumerate(cartoes, 1):
                        self.console.print(f"{i}. {cartao.nome} - {cartao.banco}")
                    
                    indice_cartao = IntPrompt.ask("Número do cartão", default=1) - 1
                    if 0 <= indice_cartao < len(cartoes):
                        cartao_id = cartoes[indice_cartao].id
            
            # Parcelamento (apenas para cartão)
            parcelas = 1
            if cartao_id:
                parcelas = IntPrompt.ask("Número de parcelas", default=1)
            
            compartilhado_com_alzi = Confirm.ask("Compartilhado com Alzi?", default=False)
            
            transacao_criada = self.client.criar_transacao(
                descricao=descricao,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                categoria=categoria if categoria else None,
                conta_id=conta_id,
                cartao_id=cartao_id,
                parcelas=parcelas,
                observacoes=observacoes if observacoes else None,
                compartilhado_com_alzi=compartilhado_com_alzi
            )
            
            if transacao_criada:
                self.console.print(f"[green]✓ Transação '{descricao}' criada com sucesso![/green]")
                if transacao_criada.eh_parcelada:
                    self.console.print(f"[blue]💳 Parcelada em {parcelas}x de R$ {transacao_criada.valor/parcelas:.2f}[/blue]")
            else:
                self.console.print("[red]✗ Erro ao criar transação[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _listar_transacoes(self):
        """Lista todas as transações"""
        self.console.print(Panel("[bold blue]📋 Lista de Transações[/bold blue]", style="blue"))
        
        try:
            transacoes = self.client.listar_transacoes()
            
            if not transacoes:
                self.console.print("[yellow]Nenhuma transação encontrada.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Data", style="cyan", width=12)
                table.add_column("Descrição", style="white", width=25)
                table.add_column("Valor", style="green", justify="right", width=12)
                table.add_column("Tipo", style="yellow", justify="center", width=8)
                table.add_column("Categoria", style="magenta", width=15)
                table.add_column("Origem", style="blue", width=15)
                table.add_column("Alzi", style="yellow", justify="center", width=6)
                
                for transacao in transacoes[:20]:  # Mostrar apenas as 20 mais recentes
                    tipo_icon = "📤" if transacao.tipo == TipoTransacao.DEBITO else "📥"
                    alzi_icon = "✓" if transacao.compartilhado_com_alzi else "✗"
                    
                    # Determinar origem
                    origem = "N/A"
                    if transacao.conta_id:
                        conta = self.client.obter_conta(transacao.conta_id)
                        origem = conta.nome if conta else "Conta"
                    elif transacao.cartao_id:
                        cartao = self.client.obter_cartao(transacao.cartao_id)
                        origem = cartao.nome if cartao else "Cartão"
                    
                    valor_str = f"R$ {transacao.valor:,.2f}"
                    if transacao.eh_parcelada:
                        valor_str += f" ({len(transacao.parcelamento)}x)"
                    
                    table.add_row(
                        transacao.data_transacao[:10],
                        transacao.descricao[:25],
                        valor_str,
                        tipo_icon,
                        transacao.categoria or "N/A",
                        origem,
                        alzi_icon
                    )
                
                self.console.print(table)
                
                if len(transacoes) > 20:
                    self.console.print(f"[dim]Mostrando 20 de {len(transacoes)} transações[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]Erro ao listar transações: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _buscar_transacoes(self):
        """Busca transações por filtros"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _editar_transacao(self):
        """Edita uma transação existente"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _excluir_transacao(self):
        """Exclui uma transação"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _transacoes_por_categoria(self):
        """Lista transações agrupadas por categoria"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _transacoes_compartilhadas_alzi(self):
        """Lista transações compartilhadas com Alzi do mês atual"""
        self.console.clear()
        self.console.print(Panel("[bold magenta]👫 Transações Compartilhadas com Alzi[/bold magenta]", style="magenta"))
        
        try:
            hoje = datetime.now()
            transacoes = self.client.obter_transacoes_mes(hoje.year, hoje.month, compartilhadas_apenas=True)
            
            if not transacoes:
                self.console.print(f"[yellow]Nenhuma transação compartilhada encontrada para {hoje.strftime('%B/%Y')}.[/yellow]")
            else:
                # Resumo
                total_debitos = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DEBITO)
                total_creditos = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.CREDITO)
                saldo_compartilhado = total_creditos - total_debitos
                
                self.console.print(f"[bold cyan]Período:[/bold cyan] {hoje.strftime('%B/%Y')}")
                self.console.print(f"[bold cyan]Total de transações:[/bold cyan] {len(transacoes)}")
                self.console.print(f"[bold red]Gastos compartilhados:[/bold red] R$ {total_debitos:,.2f}")
                self.console.print(f"[bold green]Receitas compartilhadas:[/bold green] R$ {total_creditos:,.2f}")
                self.console.print(f"[bold cyan]Saldo líquido:[/bold cyan] R$ {saldo_compartilhado:,.2f}")
                self.console.print(f"[bold cyan]Valor dividido (50%):[/bold cyan] R$ {saldo_compartilhado/2:,.2f}")
                self.console.print()
                
                # Tabela das transações
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Data", style="cyan", width=12)
                table.add_column("Descrição", style="white", width=25)
                table.add_column("Valor", style="green", justify="right", width=12)
                table.add_column("Tipo", style="yellow", justify="center", width=8)
                table.add_column("Categoria", style="yellow", width=15)
                table.add_column("Origem", style="blue", width=15)
                
                for transacao in transacoes:
                    # Mostrar todas as transações compartilhadas
                    tipo_icon = "📤" if transacao.tipo == TipoTransacao.DEBITO else "📥"
                    
                    # Determinar origem
                    origem = "N/A"
                    if transacao.conta_id:
                        conta = self.client.obter_conta(transacao.conta_id)
                        origem = conta.nome if conta else "Conta"
                    elif transacao.cartao_id:
                        cartao = self.client.obter_cartao(transacao.cartao_id)
                        origem = cartao.nome if cartao else "Cartão"
                    
                    valor_str = f"R$ {transacao.valor:,.2f}"
                    if transacao.eh_parcelada:
                        valor_str += f" ({len(transacao.parcelamento)}x)"
                    
                    table.add_row(
                        transacao.data_transacao[:10],
                        transacao.descricao,
                        valor_str,
                        tipo_icon,
                        transacao.categoria or "N/A",
                        origem
                    )
                
                self.console.print(table)
                
        except Exception as e:
            self.console.print(f"[red]Erro ao listar transações compartilhadas: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _relatorios(self):
        """Menu de relatórios e análises"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _configuracoes(self):
        """Menu de configurações"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _importar_exportar(self):
        """Menu de importação e exportação de dados"""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold blue]📤 Importar/Exportar Dados[/bold blue]", style="blue"))
            
            self.console.print("1. 📥 Importar CSV de Cartão")
            self.console.print("2. 📤 Exportar Transações")
            self.console.print("3. 📊 Histórico de Importações")
            self.console.print("M. 🔙 Voltar")
            
            opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "M", "m"])
            
            if opcao.upper() == "M":
                break
            elif opcao == "1":
                self._importar_csv_cartao()
            elif opcao == "2":
                self._exportar_transacoes()
            elif opcao == "3":
                self._historico_importacoes()

    def _importar_csv_cartao(self):
        """Importa transações de arquivo CSV de cartão"""
        self.console.clear()
        self.console.print(Panel("[bold green]📥 Importar CSV de Cartão[/bold green]", style="green"))
        
        try:
            # Listar cartões disponíveis
            cartoes = self.client.listar_cartoes()
            if not cartoes:
                self.console.print("[yellow]Nenhum cartão cadastrado. Cadastre um cartão primeiro.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Selecionar cartão
            self.console.print("[bold cyan]Cartões disponíveis:[/bold cyan]")
            for i, cartao in enumerate(cartoes, 1):
                compartilhado_icon = "👫" if cartao.compartilhado_com_alzi else "👤"
                self.console.print(f"{i}. {cartao.nome} - {cartao.banco} {compartilhado_icon}")
            
            indice_cartao = IntPrompt.ask("Número do cartão", default=1) - 1
            if not (0 <= indice_cartao < len(cartoes)):
                self.console.print("[red]Cartão inválido.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            cartao_selecionado = cartoes[indice_cartao]
            
            # Solicitar caminho do arquivo
            arquivo_path = Prompt.ask("Caminho do arquivo CSV")
            
            if not arquivo_path or not Path(arquivo_path).exists():
                self.console.print("[red]Arquivo não encontrado.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Detectar formato
            self.console.print("\n[yellow]Detectando formato do arquivo...[/yellow]")
            formato = self.client.detectar_formato_csv(arquivo_path)
            
            if not formato:
                self.console.print("[red]Formato do arquivo não reconhecido.[/red]")
                self.console.print("[dim]Formatos suportados: Bradesco[/dim]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            self.console.print(f"[green]✓ Formato detectado: {formato.upper()}[/green]")
            
            if formato != "bradesco":
                self.console.print(f"[yellow]⚠️ Apenas formato Bradesco suportado no momento.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Confirmar importação
            compartilhado_info = "Sim" if cartao_selecionado.compartilhado_com_alzi else "Não"
            self.console.print(f"\n[bold cyan]Resumo da importação:[/bold cyan]")
            self.console.print(f"Cartão: {cartao_selecionado.nome} - {cartao_selecionado.banco}")
            self.console.print(f"Compartilhado com Alzi: {compartilhado_info}")
            self.console.print(f"Arquivo: {arquivo_path}")
            self.console.print(f"Formato: {formato.upper()}")
            
            if not Confirm.ask("\nConfirmar importação?"):
                self.console.print("[yellow]Importação cancelada.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Realizar importação
            self.console.print("\n[yellow]Processando arquivo...[/yellow]")
            resultado = self.client.importar_transacoes_csv(arquivo_path, cartao_selecionado.id)
            
            # Exibir resultado
            self.console.print("\n" + "="*60)
            if resultado['sucesso']:
                self.console.print("[bold green]✓ IMPORTAÇÃO CONCLUÍDA[/bold green]")
                self.console.print(f"[cyan]Total de linhas processadas:[/cyan] {resultado['total_linhas']}")
                self.console.print(f"[cyan]Transações encontradas:[/cyan] {resultado['transacoes_encontradas']}")
                self.console.print(f"[green]Transações importadas:[/green] {resultado['transacoes_importadas']}")
                
                # Verificar se houve duplicatas
                duplicatas = resultado['transacoes_encontradas'] - resultado['transacoes_importadas']
                if duplicatas > 0:
                    self.console.print(f"[yellow]Transações duplicadas (ignoradas):[/yellow] {duplicatas}")
                
                # Exibir erros se houver
                if resultado.get('erros'):
                    self.console.print(f"\n[red]Erros encontrados ({len(resultado['erros'])}):[/red]")
                    for erro in resultado['erros'][:5]:  # Mostrar apenas os primeiros 5
                        self.console.print(f"  - {erro}")
                    if len(resultado['erros']) > 5:
                        self.console.print(f"  ... e mais {len(resultado['erros']) - 5} erros")
                
                # Informar sobre CSV limpo
                if resultado.get('csv_limpo_path'):
                    self.console.print(f"\n[blue]📄 CSV limpo gerado:[/blue] {resultado['csv_limpo_path']}")
                
            else:
                self.console.print("[bold red]✗ ERRO NA IMPORTAÇÃO[/bold red]")
                self.console.print(f"[red]Erro:[/red] {resultado.get('erro', 'Erro desconhecido')}")
            
            self.console.print("="*60)
            
        except Exception as e:
            self.console.print(f"[red]Erro durante a importação: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _exportar_transacoes(self):
        """Exporta transações para CSV"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _historico_importacoes(self):
        """Mostra histórico de importações"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _estatisticas(self):
        """Menu de estatísticas avançadas"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

# Permite executar o módulo diretamente para testes
if __name__ == "__main__":
    finance_module = FinancesModule()
    finance_module.run()