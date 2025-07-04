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
            self.console.print("5. 🗑️ Excluir Transações")
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
                self._menu_excluir_transacoes()
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
        """Lista transações com opção de visualizar por fatura"""
        self.console.clear()
        self.console.print(Panel("[bold blue]📋 Lista de Transações[/bold blue]", style="blue"))
        
        # Menu de opções
        self.console.print("1. 📅 Todas as transações recentes")
        self.console.print("2. 💳 Transações por fatura de cartão")
        self.console.print("3. 📆 Transações por período")
        
        opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3"])
        
        if opcao == "1":
            self._listar_transacoes_recentes()
        elif opcao == "2":
            self._listar_transacoes_por_fatura()
        elif opcao == "3":
            self._listar_transacoes_por_periodo()
    
    def _listar_transacoes_recentes(self):
        """Lista todas as transações recentes"""
        self.console.clear()
        self.console.print(Panel("[bold blue]📅 Transações Recentes[/bold blue]", style="blue"))
        
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
    
    def _listar_transacoes_por_fatura(self):
        """Lista transações de uma fatura específica do cartão"""
        self.console.clear()
        self.console.print(Panel("[bold red]💳 Transações por Fatura de Cartão[/bold red]", style="red"))
        
        try:
            # Listar cartões disponíveis
            cartoes = self.client.listar_cartoes()
            if not cartoes:
                self.console.print("[yellow]Nenhum cartão cadastrado.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Selecionar cartão
            self.console.print("[bold cyan]Cartões disponíveis:[/bold cyan]")
            for i, cartao in enumerate(cartoes, 1):
                self.console.print(f"{i}. {cartao.nome} - {cartao.banco} (Fecha dia {cartao.dia_fechamento}, vence dia {cartao.dia_vencimento})")
            
            indice_cartao = IntPrompt.ask("Número do cartão", default=1) - 1
            if not (0 <= indice_cartao < len(cartoes)):
                self.console.print("[red]Cartão inválido.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            cartao = cartoes[indice_cartao]
            
            # Selecionar ano
            hoje = datetime.now()
            ano_atual = hoje.year
            
            self.console.print(f"\n[cyan]Ano atual: {ano_atual}[/cyan]")
            ano_fatura = IntPrompt.ask("Ano das faturas", default=ano_atual)
            
            # Listar faturas disponíveis
            self.console.print(f"\n[yellow]Carregando faturas de {cartao.nome} para {ano_fatura}...[/yellow]")
            faturas = self.client.listar_faturas_cartao(cartao.id, ano_fatura)
            
            if not faturas:
                self.console.print(f"[yellow]Nenhuma fatura encontrada para {ano_fatura}.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Exibir faturas disponíveis
            self.console.clear()
            self.console.print(Panel(f"[bold red]💳 Faturas de {cartao.nome} - {ano_fatura}[/bold red]", style="red"))
            
            faturas_table = Table(show_header=True, header_style="bold red")
            faturas_table.add_column("#", style="yellow", width=3)
            faturas_table.add_column("Fatura", style="cyan", width=10)
            faturas_table.add_column("Período", style="white", width=25)
            faturas_table.add_column("Vencimento", style="blue", width=12)
            faturas_table.add_column("Transações", style="green", justify="center", width=12)
            faturas_table.add_column("Total", style="green", justify="right", width=15)
            faturas_table.add_column("Compartilhado", style="magenta", justify="right", width=15)
            
            for i, fatura in enumerate(faturas, 1):
                compartilhado_str = f"R$ {fatura['total_compartilhado']:,.2f}" if fatura['total_compartilhado'] > 0 else "-"
                faturas_table.add_row(
                    str(i),
                    f"{fatura['mes']:02d}/{fatura['ano']}",
                    f"{fatura['periodo_inicio']} - {fatura['periodo_fim']}",
                    fatura['vencimento'],
                    str(fatura['total_transacoes']),
                    f"R$ {fatura['total_valor']:,.2f}",
                    compartilhado_str
                )
            
            self.console.print(faturas_table)
            self.console.print("\n[bold cyan]Opções:[/bold cyan]")
            self.console.print("Digite o número da fatura para ver detalhes")
            self.console.print("Digite 'E' para editar uma transação de fatura")
            self.console.print("Digite 'M' para voltar ao menu")
            
            opcao = Prompt.ask("Escolha uma opção")
            
            if opcao.upper() == "M":
                return
            elif opcao.upper() == "E":
                self._editar_fatura_transacao(cartao, faturas)
                return
            
            try:
                indice_fatura = int(opcao) - 1
                if not (0 <= indice_fatura < len(faturas)):
                    self.console.print("[red]Fatura inválida.[/red]")
                    self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                    input()
                    return
                
                fatura_selecionada = faturas[indice_fatura]
                mes_fatura = fatura_selecionada['mes']
                ano_fatura = fatura_selecionada['ano']
                
            except ValueError:
                self.console.print("[red]Opção inválida.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Obter transações da fatura
            transacoes = self.client.obter_transacoes_fatura_cartao(cartao.id, mes_fatura, ano_fatura)
            
            if not transacoes:
                self.console.print(f"[yellow]Nenhuma transação encontrada para a fatura {mes_fatura}/{ano_fatura}.[/yellow]")
            else:
                # Calcular período da fatura
                dia_fechamento = cartao.dia_fechamento
                if mes_fatura == 1:
                    mes_inicio = 12
                    ano_inicio = ano_fatura - 1
                else:
                    mes_inicio = mes_fatura - 1
                    ano_inicio = ano_fatura
                
                self.console.print(f"\n[bold magenta]Fatura {cartao.nome} - {mes_fatura}/{ano_fatura}[/bold magenta]")
                self.console.print(f"[dim]Período: {dia_fechamento+1}/{mes_inicio}/{ano_inicio} até {dia_fechamento}/{mes_fatura}/{ano_fatura}[/dim]")
                self.console.print(f"[dim]Vencimento: {cartao.dia_vencimento}/{mes_fatura}/{ano_fatura}[/dim]\n")
                
                # Resumo da fatura
                total_fatura = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DEBITO)
                total_compartilhado = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DEBITO and t.compartilhado_com_alzi)
                
                self.console.print(f"[bold cyan]Total da fatura:[/bold cyan] R$ {total_fatura:,.2f}")
                if total_compartilhado > 0:
                    self.console.print(f"[bold magenta]Total compartilhado com Alzi:[/bold magenta] R$ {total_compartilhado:,.2f} (50% = R$ {total_compartilhado/2:,.2f})")
                self.console.print(f"[bold cyan]Total de transações:[/bold cyan] {len(transacoes)}\n")
                
                # Tabela de transações
                table = Table(show_header=True, header_style="bold red")
                table.add_column("Data", style="cyan", width=12)
                table.add_column("Descrição", style="white", width=30)
                table.add_column("Valor", style="green", justify="right", width=12)
                table.add_column("Categoria", style="magenta", width=15)
                table.add_column("Alzi", style="yellow", justify="center", width=6)
                
                # Agrupar por categoria
                categorias = {}
                for transacao in sorted(transacoes, key=lambda x: x.data_transacao):
                    alzi_icon = "✓" if transacao.compartilhado_com_alzi else "✗"
                    
                    valor_str = f"R$ {transacao.valor:,.2f}"
                    if transacao.eh_parcelada:
                        # Encontrar qual parcela é
                        for parcela in transacao.parcelamento:
                            if parcela.data_vencimento[:7] == f"{ano_fatura}-{mes_fatura:02d}":
                                valor_str = f"R$ {parcela.valor_parcela:,.2f} ({parcela.numero_parcela}/{parcela.total_parcelas})"
                                break
                    
                    table.add_row(
                        transacao.data_transacao[:10],
                        transacao.descricao[:30],
                        valor_str,
                        transacao.categoria or "Sem categoria",
                        alzi_icon
                    )
                    
                    # Agrupar por categoria
                    cat = transacao.categoria or "Sem categoria"
                    if cat not in categorias:
                        categorias[cat] = 0
                    categorias[cat] += transacao.valor
                
                self.console.print(table)
                
                # Resumo por categoria
                if len(categorias) > 1:
                    self.console.print("\n[bold cyan]Resumo por Categoria:[/bold cyan]")
                    cat_table = Table(show_header=True, header_style="bold cyan")
                    cat_table.add_column("Categoria", style="magenta")
                    cat_table.add_column("Valor Total", style="green", justify="right")
                    cat_table.add_column("% do Total", style="yellow", justify="right")
                    
                    for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                        percentual = (valor / total_fatura * 100) if total_fatura > 0 else 0
                        cat_table.add_row(cat, f"R$ {valor:,.2f}", f"{percentual:.1f}%")
                    
                    self.console.print(cat_table)
        
        except Exception as e:
            self.console.print(f"[red]Erro ao listar transações por fatura: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def _listar_transacoes_por_periodo(self):
        """Lista transações por período personalizado"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def _editar_fatura_transacao(self, cartao, faturas):
        """Permite editar qual fatura uma transação pertence"""
        self.console.clear()
        self.console.print(Panel(f"[bold yellow]✏️ Editar Fatura de Transação - {cartao.nome}[/bold yellow]", style="yellow"))
        
        try:
            # Listar todas as transações do cartão no ano
            todas_transacoes = []
            for fatura in faturas:
                todas_transacoes.extend(fatura['transacoes'])
            
            if not todas_transacoes:
                self.console.print("[yellow]Nenhuma transação encontrada.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Ordenar transações por data
            todas_transacoes.sort(key=lambda x: x.data_transacao, reverse=True)
            
            # Exibir transações para seleção
            self.console.print("[bold cyan]Transações disponíveis:[/bold cyan]")
            transacoes_table = Table(show_header=True, header_style="bold yellow")
            transacoes_table.add_column("#", style="yellow", width=3)
            transacoes_table.add_column("Data", style="cyan", width=12)
            transacoes_table.add_column("Descrição", style="white", width=30)
            transacoes_table.add_column("Valor", style="green", justify="right", width=12)
            transacoes_table.add_column("Fatura Atual", style="blue", width=12)
            
            # Determinar fatura atual de cada transação
            for i, transacao in enumerate(todas_transacoes[:20], 1):  # Mostrar apenas 20
                # Encontrar a qual fatura pertence
                fatura_atual = "N/A"
                for fatura in faturas:
                    if transacao in fatura['transacoes']:
                        fatura_atual = f"{fatura['mes']:02d}/{fatura['ano']}"
                        break
                
                transacoes_table.add_row(
                    str(i),
                    transacao.data_transacao[:10],
                    transacao.descricao[:30],
                    f"R$ {transacao.valor:,.2f}",
                    fatura_atual
                )
            
            self.console.print(transacoes_table)
            
            if len(todas_transacoes) > 20:
                self.console.print(f"[dim]Mostrando 20 de {len(todas_transacoes)} transações[/dim]")
            
            # Selecionar transação
            self.console.print("\n[bold cyan]Selecionar transação:[/bold cyan]")
            indice_transacao = IntPrompt.ask("Número da transação para editar", default=1) - 1
            
            if not (0 <= indice_transacao < min(20, len(todas_transacoes))):
                self.console.print("[red]Transação inválida.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            transacao_selecionada = todas_transacoes[indice_transacao]
            
            # Exibir faturas disponíveis para mover
            self.console.print(f"\n[bold cyan]Movendo transação: {transacao_selecionada.descricao}[/bold cyan]")
            self.console.print("[bold cyan]Faturas disponíveis:[/bold cyan]")
            
            for i, fatura in enumerate(faturas, 1):
                self.console.print(f"{i}. {fatura['mes']:02d}/{fatura['ano']} - R$ {fatura['total_valor']:,.2f}")
            
            # Selecionar nova fatura
            indice_nova_fatura = IntPrompt.ask("Número da fatura de destino", default=1) - 1
            
            if not (0 <= indice_nova_fatura < len(faturas)):
                self.console.print("[red]Fatura inválida.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            nova_fatura = faturas[indice_nova_fatura]
            
            # Calcular nova data para a transação (baseada no período da fatura)
            # Vamos colocar a transação no meio do período da fatura
            periodo_inicio = datetime.strptime(nova_fatura['periodo_inicio'], "%d/%m/%Y")
            periodo_fim = datetime.strptime(nova_fatura['periodo_fim'], "%d/%m/%Y")
            
            # Calcular data no meio do período
            dias_diferenca = (periodo_fim - periodo_inicio).days
            nova_data = periodo_inicio + timedelta(days=dias_diferenca // 2)
            nova_data_str = nova_data.strftime("%Y-%m-%d")
            
            # Confirmar a mudança
            self.console.print(f"\n[bold yellow]Confirmação da alteração:[/bold yellow]")
            self.console.print(f"Transação: {transacao_selecionada.descricao}")
            self.console.print(f"Data atual: {transacao_selecionada.data_transacao[:10]}")
            self.console.print(f"Nova data: {nova_data_str}")
            self.console.print(f"Nova fatura: {nova_fatura['mes']:02d}/{nova_fatura['ano']}")
            
            if Confirm.ask("\nConfirmar alteração?"):
                # Atualizar a transação
                sucesso = self.client.atualizar_transacao(
                    transacao_selecionada.id,
                    data_transacao=nova_data_str
                )
                
                if sucesso:
                    self.console.print(f"[green]✓ Transação movida para a fatura {nova_fatura['mes']:02d}/{nova_fatura['ano']} com sucesso![/green]")
                else:
                    self.console.print("[red]✗ Erro ao atualizar transação[/red]")
            else:
                self.console.print("[yellow]Alteração cancelada.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Erro ao editar fatura da transação: {e}[/red]")
        
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

    def _menu_excluir_transacoes(self):
        """Menu de opções para exclusão de transações"""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold red]🗑️ Excluir Transações[/bold red]", style="red"))
            
            self.console.print("1. 🎯 Excluir transação individual")
            self.console.print("2. 📋 Excluir múltiplas transações (seleção)")
            self.console.print("3. 💳 Excluir por fatura de cartão")
            self.console.print("4. 🧹 Excluir fatura completa")
            self.console.print("M. 🔙 Voltar")
            
            opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "4", "M", "m"])
            
            if opcao.upper() == "M":
                break
            elif opcao == "1":
                self._excluir_transacao_individual()
            elif opcao == "2":
                self._excluir_transacoes_multiplas()
            elif opcao == "3":
                self._excluir_transacoes_por_fatura()
            elif opcao == "4":
                self._excluir_fatura_completa()
    
    def _excluir_transacao_individual(self):
        """Exclui uma transação específica"""
        self.console.clear()
        self.console.print(Panel("[bold red]🎯 Excluir Transação Individual[/bold red]", style="red"))
        
        try:
            # Listar transações recentes
            transacoes = self.client.listar_transacoes()
            
            if not transacoes:
                self.console.print("[yellow]Nenhuma transação encontrada.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Mostrar transações
            self.console.print("[bold cyan]Transações disponíveis:[/bold cyan]")
            transacoes_table = Table(show_header=True, header_style="bold red")
            transacoes_table.add_column("#", style="yellow", width=3)
            transacoes_table.add_column("Data", style="cyan", width=12)
            transacoes_table.add_column("Descrição", style="white", width=30)
            transacoes_table.add_column("Valor", style="green", justify="right", width=12)
            transacoes_table.add_column("Origem", style="blue", width=15)
            
            for i, transacao in enumerate(transacoes[:20], 1):  # Mostrar apenas 20
                # Determinar origem
                origem = "N/A"
                if transacao.conta_id:
                    conta = self.client.obter_conta(transacao.conta_id)
                    origem = conta.nome if conta else "Conta"
                elif transacao.cartao_id:
                    cartao = self.client.obter_cartao(transacao.cartao_id)
                    origem = cartao.nome if cartao else "Cartão"
                
                transacoes_table.add_row(
                    str(i),
                    transacao.data_transacao[:10],
                    transacao.descricao[:30],
                    f"R$ {transacao.valor:,.2f}",
                    origem
                )
            
            self.console.print(transacoes_table)
            
            if len(transacoes) > 20:
                self.console.print(f"[dim]Mostrando 20 de {len(transacoes)} transações[/dim]")
            
            # Selecionar transação
            indice = IntPrompt.ask("Número da transação para excluir (0 para cancelar)", default=0)
            
            if indice == 0:
                self.console.print("[yellow]Operação cancelada.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            if not (1 <= indice <= min(20, len(transacoes))):
                self.console.print("[red]Número inválido.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            transacao_selecionada = transacoes[indice - 1]
            
            # Confirmar exclusão
            self.console.print(f"\n[bold yellow]Confirmar exclusão:[/bold yellow]")
            self.console.print(f"Transação: {transacao_selecionada.descricao}")
            self.console.print(f"Valor: R$ {transacao_selecionada.valor:,.2f}")
            self.console.print(f"Data: {transacao_selecionada.data_transacao[:10]}")
            
            if Confirm.ask("\nTem certeza que deseja excluir esta transação?"):
                sucesso = self.client.excluir_transacao(transacao_selecionada.id)
                
                if sucesso:
                    self.console.print(f"[green]✅ Transação excluída com sucesso![/green]")
                    self.console.print(f"[blue]💡 Limites/saldos ajustados automaticamente[/blue]")
                else:
                    self.console.print("[red]❌ Erro ao excluir transação[/red]")
            else:
                self.console.print("[yellow]Exclusão cancelada.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def _excluir_transacoes_multiplas(self):
        """Exclui múltiplas transações por seleção"""
        self.console.clear()
        self.console.print(Panel("[bold red]📋 Excluir Múltiplas Transações[/bold red]", style="red"))
        
        try:
            # Listar transações recentes
            transacoes = self.client.listar_transacoes()
            
            if not transacoes:
                self.console.print("[yellow]Nenhuma transação encontrada.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Mostrar transações
            self.console.print("[bold cyan]Transações disponíveis:[/bold cyan]")
            transacoes_table = Table(show_header=True, header_style="bold red")
            transacoes_table.add_column("#", style="yellow", width=3)
            transacoes_table.add_column("Data", style="cyan", width=12)
            transacoes_table.add_column("Descrição", style="white", width=25)
            transacoes_table.add_column("Valor", style="green", justify="right", width=12)
            transacoes_table.add_column("Origem", style="blue", width=15)
            
            for i, transacao in enumerate(transacoes[:30], 1):  # Mostrar até 30
                # Determinar origem
                origem = "N/A"
                if transacao.conta_id:
                    conta = self.client.obter_conta(transacao.conta_id)
                    origem = conta.nome if conta else "Conta"
                elif transacao.cartao_id:
                    cartao = self.client.obter_cartao(transacao.cartao_id)
                    origem = cartao.nome if cartao else "Cartão"
                
                transacoes_table.add_row(
                    str(i),
                    transacao.data_transacao[:10],
                    transacao.descricao[:25],
                    f"R$ {transacao.valor:,.2f}",
                    origem
                )
            
            self.console.print(transacoes_table)
            
            if len(transacoes) > 30:
                self.console.print(f"[dim]Mostrando 30 de {len(transacoes)} transações[/dim]")
            
            # Selecionar múltiplas transações
            self.console.print("\n[bold cyan]Seleção múltipla:[/bold cyan]")
            self.console.print("[dim]Digite os números separados por vírgula (ex: 1,3,5-8,10)[/dim]")
            self.console.print("[dim]Ou digite 'todos' para selecionar todas visíveis[/dim]")
            
            selecao = Prompt.ask("Números das transações para excluir")
            
            if selecao.lower() == "todos":
                indices_selecionados = list(range(1, min(31, len(transacoes) + 1)))
            else:
                try:
                    indices_selecionados = []
                    for parte in selecao.split(','):
                        parte = parte.strip()
                        if '-' in parte:
                            inicio, fim = map(int, parte.split('-'))
                            indices_selecionados.extend(range(inicio, fim + 1))
                        else:
                            indices_selecionados.append(int(parte))
                    
                    # Remover duplicatas e ordenar
                    indices_selecionados = sorted(set(indices_selecionados))
                    
                except ValueError:
                    self.console.print("[red]Formato inválido.[/red]")
                    self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                    input()
                    return
            
            # Validar índices
            indices_validos = [i for i in indices_selecionados if 1 <= i <= min(30, len(transacoes))]
            
            if not indices_validos:
                self.console.print("[red]Nenhuma transação válida selecionada.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            transacoes_selecionadas = [transacoes[i - 1] for i in indices_validos]
            
            # Mostrar resumo da seleção
            total_valor = sum(t.valor for t in transacoes_selecionadas)
            self.console.print(f"\n[bold yellow]Resumo da seleção:[/bold yellow]")
            self.console.print(f"Transações selecionadas: {len(transacoes_selecionadas)}")
            self.console.print(f"Valor total: R$ {total_valor:,.2f}")
            
            # Confirmar exclusão
            if Confirm.ask(f"\nTem certeza que deseja excluir {len(transacoes_selecionadas)} transações?"):
                transacao_ids = [t.id for t in transacoes_selecionadas]
                resultado = self.client.excluir_multiplas_transacoes(transacao_ids)
                
                # Exibir resultado
                self.console.print(f"\n[bold cyan]Resultado da exclusão:[/bold cyan]")
                self.console.print(f"Solicitadas: {resultado['total_solicitadas']}")
                self.console.print(f"[green]Excluídas: {resultado['excluidas']}[/green]")
                
                if resultado['erros']:
                    self.console.print(f"[red]Erros: {len(resultado['erros'])}[/red]")
                    for erro in resultado['erros'][:3]:  # Mostrar apenas os primeiros 3 erros
                        self.console.print(f"  - {erro}")
                
                if resultado['sucesso']:
                    self.console.print(f"[green]✅ Exclusão concluída com sucesso![/green]")
                    self.console.print(f"[blue]💡 Limites/saldos ajustados automaticamente[/blue]")
                else:
                    self.console.print(f"[yellow]⚠️ Exclusão parcialmente bem-sucedida[/yellow]")
            else:
                self.console.print("[yellow]Exclusão cancelada.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def _excluir_transacoes_por_fatura(self):
        """Exclui transações selecionadas de uma fatura específica"""
        self.console.clear()
        self.console.print(Panel("[bold red]💳 Excluir Transações por Fatura[/bold red]", style="red"))
        
        try:
            # Selecionar cartão e fatura (reutilizar lógica existente)
            cartoes = self.client.listar_cartoes()
            if not cartoes:
                self.console.print("[yellow]Nenhum cartão cadastrado.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Selecionar cartão
            self.console.print("[bold cyan]Cartões disponíveis:[/bold cyan]")
            for i, cartao in enumerate(cartoes, 1):
                self.console.print(f"{i}. {cartao.nome} - {cartao.banco}")
            
            indice_cartao = IntPrompt.ask("Número do cartão", default=1) - 1
            if not (0 <= indice_cartao < len(cartoes)):
                self.console.print("[red]Cartão inválido.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            cartao = cartoes[indice_cartao]
            
            # Selecionar ano e listar faturas
            hoje = datetime.now()
            ano_fatura = IntPrompt.ask("Ano das faturas", default=hoje.year)
            
            faturas = self.client.listar_faturas_cartao(cartao.id, ano_fatura)
            
            if not faturas:
                self.console.print(f"[yellow]Nenhuma fatura encontrada para {ano_fatura}.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Mostrar faturas
            self.console.print(f"\n[bold cyan]Faturas de {cartao.nome} - {ano_fatura}:[/bold cyan]")
            for i, fatura in enumerate(faturas, 1):
                self.console.print(f"{i}. {fatura['mes']:02d}/{fatura['ano']} - {fatura['total_transacoes']} transações - R$ {fatura['total_valor']:,.2f}")
            
            indice_fatura = IntPrompt.ask("Número da fatura", default=1) - 1
            if not (0 <= indice_fatura < len(faturas)):
                self.console.print("[red]Fatura inválida.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            fatura_selecionada = faturas[indice_fatura]
            transacoes_fatura = fatura_selecionada['transacoes']
            
            # Mostrar transações da fatura
            self.console.print(f"\n[bold cyan]Transações da fatura {fatura_selecionada['mes']:02d}/{fatura_selecionada['ano']}:[/bold cyan]")
            
            transacoes_table = Table(show_header=True, header_style="bold red")
            transacoes_table.add_column("#", style="yellow", width=3)
            transacoes_table.add_column("Data", style="cyan", width=12)
            transacoes_table.add_column("Descrição", style="white", width=30)
            transacoes_table.add_column("Valor", style="green", justify="right", width=12)
            
            for i, transacao in enumerate(transacoes_fatura, 1):
                transacoes_table.add_row(
                    str(i),
                    transacao.data_transacao[:10],
                    transacao.descricao[:30],
                    f"R$ {transacao.valor:,.2f}"
                )
            
            self.console.print(transacoes_table)
            
            # Seleção de transações (similar ao método anterior)
            self.console.print("\n[bold cyan]Seleção:[/bold cyan]")
            self.console.print("[dim]Digite os números separados por vírgula (ex: 1,3,5-8,10)[/dim]")
            self.console.print("[dim]Ou digite 'todos' para selecionar todas[/dim]")
            
            selecao = Prompt.ask("Números das transações para excluir")
            
            if selecao.lower() == "todos":
                transacoes_selecionadas = transacoes_fatura
            else:
                try:
                    indices_selecionados = []
                    for parte in selecao.split(','):
                        parte = parte.strip()
                        if '-' in parte:
                            inicio, fim = map(int, parte.split('-'))
                            indices_selecionados.extend(range(inicio, fim + 1))
                        else:
                            indices_selecionados.append(int(parte))
                    
                    indices_selecionados = sorted(set(indices_selecionados))
                    indices_validos = [i for i in indices_selecionados if 1 <= i <= len(transacoes_fatura)]
                    transacoes_selecionadas = [transacoes_fatura[i - 1] for i in indices_validos]
                    
                except ValueError:
                    self.console.print("[red]Formato inválido.[/red]")
                    self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                    input()
                    return
            
            if not transacoes_selecionadas:
                self.console.print("[red]Nenhuma transação selecionada.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Confirmar e executar exclusão
            total_valor = sum(t.valor for t in transacoes_selecionadas)
            self.console.print(f"\n[bold yellow]Confirmar exclusão:[/bold yellow]")
            self.console.print(f"Fatura: {fatura_selecionada['mes']:02d}/{fatura_selecionada['ano']}")
            self.console.print(f"Transações: {len(transacoes_selecionadas)}")
            self.console.print(f"Valor total: R$ {total_valor:,.2f}")
            
            if Confirm.ask("\nConfirmar exclusão?"):
                transacao_ids = [t.id for t in transacoes_selecionadas]
                resultado = self.client.excluir_multiplas_transacoes(transacao_ids)
                
                self.console.print(f"\n[bold cyan]Resultado:[/bold cyan]")
                self.console.print(f"[green]Excluídas: {resultado['excluidas']}/{resultado['total_solicitadas']}[/green]")
                
                if resultado['erros']:
                    self.console.print(f"[red]Erros: {len(resultado['erros'])}[/red]")
                
                if resultado['sucesso']:
                    self.console.print(f"[green]✅ Exclusão concluída![/green]")
                else:
                    self.console.print(f"[yellow]⚠️ Exclusão parcial[/yellow]")
            else:
                self.console.print("[yellow]Exclusão cancelada.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def _excluir_fatura_completa(self):
        """Exclui uma fatura completa de um cartão"""
        self.console.clear()
        self.console.print(Panel("[bold red]🧹 Excluir Fatura Completa[/bold red]", style="red"))
        
        try:
            # Selecionar cartão
            cartoes = self.client.listar_cartoes()
            if not cartoes:
                self.console.print("[yellow]Nenhum cartão cadastrado.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            self.console.print("[bold cyan]Cartões disponíveis:[/bold cyan]")
            for i, cartao in enumerate(cartoes, 1):
                self.console.print(f"{i}. {cartao.nome} - {cartao.banco}")
            
            indice_cartao = IntPrompt.ask("Número do cartão", default=1) - 1
            if not (0 <= indice_cartao < len(cartoes)):
                self.console.print("[red]Cartão inválido.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            cartao = cartoes[indice_cartao]
            
            # Selecionar ano e listar faturas
            hoje = datetime.now()
            ano_fatura = IntPrompt.ask("Ano das faturas", default=hoje.year)
            
            faturas = self.client.listar_faturas_cartao(cartao.id, ano_fatura)
            
            if not faturas:
                self.console.print(f"[yellow]Nenhuma fatura encontrada para {ano_fatura}.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Mostrar faturas com detalhes
            self.console.print(f"\n[bold cyan]Faturas de {cartao.nome} - {ano_fatura}:[/bold cyan]")
            
            faturas_table = Table(show_header=True, header_style="bold red")
            faturas_table.add_column("#", style="yellow", width=3)
            faturas_table.add_column("Fatura", style="cyan", width=10)
            faturas_table.add_column("Transações", style="blue", justify="center", width=12)
            faturas_table.add_column("Total", style="green", justify="right", width=15)
            faturas_table.add_column("Compartilhado", style="magenta", justify="right", width=15)
            
            for i, fatura in enumerate(faturas, 1):
                compartilhado_str = f"R$ {fatura['total_compartilhado']:,.2f}" if fatura['total_compartilhado'] > 0 else "-"
                faturas_table.add_row(
                    str(i),
                    f"{fatura['mes']:02d}/{fatura['ano']}",
                    str(fatura['total_transacoes']),
                    f"R$ {fatura['total_valor']:,.2f}",
                    compartilhado_str
                )
            
            self.console.print(faturas_table)
            
            # Selecionar fatura
            indice_fatura = IntPrompt.ask("Número da fatura para excluir completamente", default=1) - 1
            if not (0 <= indice_fatura < len(faturas)):
                self.console.print("[red]Fatura inválida.[/red]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            fatura_selecionada = faturas[indice_fatura]
            
            # Confirmação com detalhes
            self.console.print(f"\n[bold red]⚠️ ATENÇÃO - EXCLUSÃO PERMANENTE ⚠️[/bold red]")
            self.console.print(f"[bold yellow]Fatura selecionada:[/bold yellow]")
            self.console.print(f"Cartão: {cartao.nome}")
            self.console.print(f"Fatura: {fatura_selecionada['mes']:02d}/{fatura_selecionada['ano']}")
            self.console.print(f"Transações: {fatura_selecionada['total_transacoes']}")
            self.console.print(f"Valor total: R$ {fatura_selecionada['total_valor']:,.2f}")
            
            if fatura_selecionada['total_compartilhado'] > 0:
                self.console.print(f"Valor compartilhado: R$ {fatura_selecionada['total_compartilhado']:,.2f}")
            
            self.console.print(f"\n[red]Esta ação irá excluir TODAS as {fatura_selecionada['total_transacoes']} transações da fatura![/red]")
            
            if Confirm.ask("\nTem CERTEZA ABSOLUTA que deseja excluir esta fatura completa?"):
                # Executar exclusão
                resultado = self.client.excluir_fatura_completa(
                    cartao.id, 
                    fatura_selecionada['mes'], 
                    fatura_selecionada['ano']
                )
                
                # Exibir resultado detalhado
                self.console.print(f"\n[bold cyan]Resultado da exclusão:[/bold cyan]")
                self.console.print(f"Fatura: {resultado['mes_fatura']:02d}/{resultado['ano_fatura']}")
                self.console.print(f"Transações na fatura: {resultado['total_transacoes']}")
                self.console.print(f"[green]Transações excluídas: {resultado['excluidas']}[/green]")
                
                if resultado['erros']:
                    self.console.print(f"[red]Erros ocorridos: {len(resultado['erros'])}[/red]")
                    for erro in resultado['erros'][:3]:
                        self.console.print(f"  - {erro}")
                
                if resultado['sucesso']:
                    self.console.print(f"\n[green]✅ Fatura {resultado['mes_fatura']:02d}/{resultado['ano_fatura']} excluída completamente![/green]")
                    self.console.print(f"[blue]💡 Limite do cartão restaurado automaticamente[/blue]")
                else:
                    self.console.print(f"\n[yellow]⚠️ Exclusão parcialmente bem-sucedida[/yellow]")
            else:
                self.console.print("[yellow]Exclusão cancelada.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _transacoes_por_categoria(self):
        """Lista transações agrupadas por categoria"""
        self.console.print("[yellow]Funcionalidade em desenvolvimento...[/yellow]")
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()

    def _transacoes_compartilhadas_alzi(self):
        """Menu de transações compartilhadas com Alzi"""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold magenta]👫 Transações Compartilhadas com Alzi[/bold magenta]", style="magenta"))
            
            self.console.print("1. 📅 Fatura atual (período ativo)")
            self.console.print("2. 💳 Visão por fatura de cartão")
            self.console.print("3. 📊 Histórico mensal")
            self.console.print("M. 🔙 Voltar")
            
            opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "M", "m"])
            
            if opcao.upper() == "M":
                break
            elif opcao == "1":
                self._visualizar_compartilhado_mensal()
            elif opcao == "2":
                self._visualizar_compartilhado_por_fatura()
            elif opcao == "3":
                self._historico_compartilhado_mensal()
    
    def _visualizar_compartilhado_mensal(self):
        """Visualiza transações compartilhadas da fatura atual"""
        self.console.clear()
        self.console.print(Panel("[bold magenta]📅 Transações Compartilhadas - Fatura Atual[/bold magenta]", style="magenta"))
        
        try:
            hoje = datetime.now()
            
            # Primeiro, vamos encontrar a fatura atual baseada na data de hoje
            # Obter cartões compartilhados
            cartoes_compartilhados = [c for c in self.client.listar_cartoes() if c.compartilhado_com_alzi]
            
            if not cartoes_compartilhados:
                self.console.print("[yellow]Nenhum cartão compartilhado com Alzi encontrado.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Usar o primeiro cartão compartilhado para determinar a fatura atual
            cartao = cartoes_compartilhados[0]
            
            # Calcular qual fatura estamos vivendo agora
            # Baseado na lógica do cartão (fechamento dia 20, vencimento dia 1)
            # Se hoje é 06/06 e fechamento é dia 20, estamos no período da fatura 07/2025
            # (período 21/05 a 20/06, vence 01/07)
            dia_fechamento = cartao.dia_fechamento
            
            if hoje.day > dia_fechamento:
                # Estamos após o fechamento, então começou o período da próxima fatura
                # Ex: 25/06 → período da fatura que vence em 08/2025
                if hoje.month == 12:
                    mes_fatura_atual = 2  # Jan + 1 = Fev (próximo ano)
                    ano_fatura_atual = hoje.year + 1
                elif hoje.month == 11:
                    mes_fatura_atual = 1  # Dez + 1 = Jan (próximo ano)
                    ano_fatura_atual = hoje.year + 1
                else:
                    mes_fatura_atual = hoje.month + 2
                    ano_fatura_atual = hoje.year
            else:
                # Estamos antes/no dia do fechamento, então estamos no período da fatura atual
                # Ex: 06/06 → período da fatura que vence em 07/2025
                if hoje.month == 12:
                    mes_fatura_atual = 1
                    ano_fatura_atual = hoje.year + 1
                else:
                    mes_fatura_atual = hoje.month + 1
                    ano_fatura_atual = hoje.year
            
            # Obter transações da fatura atual
            transacoes = self.client.obter_transacoes_fatura_cartao(cartao.id, mes_fatura_atual, ano_fatura_atual)
            transacoes_compartilhadas = [t for t in transacoes if t.compartilhado_com_alzi]
            
            # Se houver múltiplos cartões compartilhados, agregar todas as transações
            if len(cartoes_compartilhados) > 1:
                for cartao_adicional in cartoes_compartilhados[1:]:
                    transacoes_adicionais = self.client.obter_transacoes_fatura_cartao(cartao_adicional.id, mes_fatura_atual, ano_fatura_atual)
                    transacoes_compartilhadas.extend([t for t in transacoes_adicionais if t.compartilhado_com_alzi])
            
            meses_nomes = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                          "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            
            nome_mes_fatura = meses_nomes[mes_fatura_atual]
            
            self.console.print(f"[bold cyan]Fatura atual:[/bold cyan] {nome_mes_fatura}/{ano_fatura_atual}")
            self.console.print(f"[bold cyan]Fechamento:[/bold cyan] Dia {dia_fechamento} de cada mês")
            
            if not transacoes_compartilhadas:
                self.console.print(f"[yellow]Nenhuma transação compartilhada encontrada na fatura atual ({nome_mes_fatura}/{ano_fatura_atual}).[/yellow]")
            else:
                # Resumo
                total_debitos = sum(t.valor for t in transacoes_compartilhadas if t.tipo == TipoTransacao.DEBITO)
                total_creditos = sum(t.valor for t in transacoes_compartilhadas if t.tipo == TipoTransacao.CREDITO)
                saldo_compartilhado = total_creditos - total_debitos
                
                # Calcular período da fatura
                # Se estamos antes do fechamento, mostramos o período que começou no mês passado
                if hoje.day > dia_fechamento:
                    # Período atual: (mês atual, dia fechamento+1) até (próximo mês, dia fechamento)
                    if hoje.month == 12:
                        data_inicio = f"{dia_fechamento+1}/{hoje.month}/{hoje.year}"
                        data_fim = f"{dia_fechamento}/01/{hoje.year+1}"
                    else:
                        data_inicio = f"{dia_fechamento+1}/{hoje.month}/{hoje.year}"
                        data_fim = f"{dia_fechamento}/{hoje.month+1}/{hoje.year}"
                else:
                    # Período atual: (mês passado, dia fechamento+1) até (mês atual, dia fechamento)  
                    if hoje.month == 1:
                        data_inicio = f"{dia_fechamento+1}/12/{hoje.year-1}"
                        data_fim = f"{dia_fechamento}/{hoje.month}/{hoje.year}"
                    else:
                        data_inicio = f"{dia_fechamento+1}/{hoje.month-1}/{hoje.year}"
                        data_fim = f"{dia_fechamento}/{hoje.month}/{hoje.year}"
                
                self.console.print(f"[bold cyan]Período da fatura:[/bold cyan] {data_inicio} até {data_fim}")
                self.console.print(f"[bold cyan]Total de transações compartilhadas:[/bold cyan] {len(transacoes_compartilhadas)}")
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
                
                for transacao in transacoes_compartilhadas:
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
    
    def _visualizar_compartilhado_por_fatura(self):
        """Visualiza transações compartilhadas por fatura de cartão"""
        self.console.clear()
        self.console.print(Panel("[bold magenta]💳 Transações Compartilhadas por Fatura[/bold magenta]", style="magenta"))
        
        try:
            # Listar apenas cartões compartilhados com Alzi
            cartoes = [c for c in self.client.listar_cartoes() if c.compartilhado_com_alzi]
            
            if not cartoes:
                self.console.print("[yellow]Nenhum cartão compartilhado com Alzi encontrado.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Se houver apenas um cartão compartilhado, selecionar automaticamente
            if len(cartoes) == 1:
                cartao = cartoes[0]
                self.console.print(f"[cyan]Cartão selecionado automaticamente: {cartao.nome}[/cyan]\n")
            else:
                # Mostrar cartões compartilhados para seleção
                self.console.print("[bold cyan]Cartões compartilhados com Alzi:[/bold cyan]")
                for i, cartao in enumerate(cartoes, 1):
                    self.console.print(f"{i}. {cartao.nome} - {cartao.banco} (Vence dia {cartao.dia_vencimento})")
                
                indice_cartao = IntPrompt.ask("Número do cartão", default=1) - 1
                if not (0 <= indice_cartao < len(cartoes)):
                    self.console.print("[red]Cartão inválido.[/red]")
                    self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                    input()
                    return
                
                cartao = cartoes[indice_cartao]
            
            # Selecionar ano
            hoje = datetime.now()
            ano_atual = hoje.year
            
            self.console.print(f"\n[cyan]Ano atual: {ano_atual}[/cyan]")
            ano_fatura = IntPrompt.ask("Ano das faturas", default=ano_atual)
            
            # Obter todas as faturas do cartão
            faturas = self.client.listar_faturas_cartao(cartao.id, ano_fatura)
            
            if not faturas:
                self.console.print(f"[yellow]Nenhuma fatura encontrada para {ano_fatura}.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Filtrar apenas faturas com transações compartilhadas
            faturas_compartilhadas = []
            for fatura in faturas:
                transacoes_compartilhadas = [t for t in fatura['transacoes'] if t.compartilhado_com_alzi]
                if transacoes_compartilhadas:
                    fatura_compartilhada = fatura.copy()
                    fatura_compartilhada['transacoes_compartilhadas'] = transacoes_compartilhadas
                    fatura_compartilhada['total_compartilhado_calculado'] = sum(
                        t.valor for t in transacoes_compartilhadas if t.tipo == TipoTransacao.DEBITO
                    )
                    faturas_compartilhadas.append(fatura_compartilhada)
            
            if not faturas_compartilhadas:
                self.console.print(f"[yellow]Nenhuma fatura compartilhada encontrada para {ano_fatura}.[/yellow]")
                self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                input()
                return
            
            # Exibir resumo das faturas compartilhadas
            self.console.clear()
            self.console.print(Panel(f"[bold magenta]💳 Faturas Compartilhadas - {cartao.nome} ({ano_fatura})[/bold magenta]", style="magenta"))
            
            # Calcular totais do ano
            total_ano = sum(f['total_compartilhado_calculado'] for f in faturas_compartilhadas)
            
            self.console.print(f"[bold cyan]Total compartilhado no ano:[/bold cyan] R$ {total_ano:,.2f}")
            self.console.print(f"[bold cyan]Valor dividido (50%):[/bold cyan] R$ {total_ano/2:,.2f}")
            self.console.print(f"[bold cyan]Média mensal:[/bold cyan] R$ {total_ano/len(faturas_compartilhadas):,.2f}\n")
            
            # Tabela resumo das faturas
            faturas_table = Table(show_header=True, header_style="bold magenta")
            faturas_table.add_column("#", style="yellow", width=3)
            faturas_table.add_column("Fatura", style="cyan", width=10)
            faturas_table.add_column("Período", style="white", width=25)
            faturas_table.add_column("Transações", style="blue", justify="center", width=12)
            faturas_table.add_column("Total Compartilhado", style="green", justify="right", width=18)
            faturas_table.add_column("50%", style="magenta", justify="right", width=12)
            
            for i, fatura in enumerate(faturas_compartilhadas, 1):
                faturas_table.add_row(
                    str(i),
                    f"{fatura['mes']:02d}/{fatura['ano']}",
                    f"{fatura['periodo_inicio']} - {fatura['periodo_fim']}",
                    str(len(fatura['transacoes_compartilhadas'])),
                    f"R$ {fatura['total_compartilhado_calculado']:,.2f}",
                    f"R$ {fatura['total_compartilhado_calculado']/2:,.2f}"
                )
            
            self.console.print(faturas_table)
            
            # Opção para ver detalhes
            self.console.print("\n[bold cyan]Digite o número da fatura para ver detalhes ou 'M' para voltar[/bold cyan]")
            opcao = Prompt.ask("Escolha uma opção")
            
            if opcao.upper() != "M":
                try:
                    indice_fatura = int(opcao) - 1
                    if 0 <= indice_fatura < len(faturas_compartilhadas):
                        self._detalhar_fatura_compartilhada(cartao, faturas_compartilhadas[indice_fatura])
                    else:
                        self.console.print("[red]Fatura inválida.[/red]")
                        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                        input()
                except ValueError:
                    self.console.print("[red]Opção inválida.[/red]")
                    self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
                    input()
                    
        except Exception as e:
            self.console.print(f"[red]Erro ao listar faturas compartilhadas: {e}[/red]")
            self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
            input()
    
    def _detalhar_fatura_compartilhada(self, cartao, fatura):
        """Exibe detalhes de uma fatura compartilhada específica"""
        self.console.clear()
        self.console.print(Panel(f"[bold magenta]📋 Detalhes da Fatura Compartilhada - {fatura['mes']:02d}/{fatura['ano']}[/bold magenta]", style="magenta"))
        
        try:
            # Informações da fatura
            self.console.print(f"[bold cyan]Cartão:[/bold cyan] {cartao.nome} - {cartao.banco}")
            self.console.print(f"[bold cyan]Período:[/bold cyan] {fatura['periodo_inicio']} até {fatura['periodo_fim']}")
            self.console.print(f"[bold cyan]Vencimento:[/bold cyan] {fatura['vencimento']}")
            self.console.print()
            
            # Resumo financeiro
            transacoes = fatura['transacoes_compartilhadas']
            total_compartilhado = fatura['total_compartilhado_calculado']
            
            self.console.print(f"[bold green]Total compartilhado:[/bold green] R$ {total_compartilhado:,.2f}")
            self.console.print(f"[bold magenta]Valor dividido (50%):[/bold magenta] R$ {total_compartilhado/2:,.2f}")
            self.console.print(f"[bold cyan]Total de transações compartilhadas:[/bold cyan] {len(transacoes)}")
            self.console.print()
            
            # Tabela de transações
            table = Table(show_header=True, header_style="bold magenta", title="Transações Compartilhadas")
            table.add_column("Data", style="cyan", width=12)
            table.add_column("Descrição", style="white", width=35)
            table.add_column("Valor", style="green", justify="right", width=12)
            table.add_column("Categoria", style="yellow", width=15)
            
            # Agrupar por categoria
            categorias = {}
            
            for transacao in sorted(transacoes, key=lambda x: x.data_transacao):
                valor_str = f"R$ {transacao.valor:,.2f}"
                if transacao.eh_parcelada:
                    # Encontrar qual parcela é desta fatura
                    for parcela in transacao.parcelamento:
                        if parcela.data_vencimento[:7] == f"{fatura['ano']}-{fatura['mes']:02d}":
                            valor_str = f"R$ {parcela.valor_parcela:,.2f} ({parcela.numero_parcela}/{parcela.total_parcelas})"
                            break
                
                table.add_row(
                    transacao.data_transacao[:10],
                    transacao.descricao[:35],
                    valor_str,
                    transacao.categoria or "Sem categoria"
                )
                
                # Somar por categoria
                cat = transacao.categoria or "Sem categoria"
                if cat not in categorias:
                    categorias[cat] = 0
                categorias[cat] += transacao.valor
            
            self.console.print(table)
            
            # Resumo por categoria
            if len(categorias) > 1:
                self.console.print("\n[bold cyan]Resumo por Categoria:[/bold cyan]")
                cat_table = Table(show_header=True, header_style="bold cyan")
                cat_table.add_column("Categoria", style="yellow")
                cat_table.add_column("Valor Total", style="green", justify="right")
                cat_table.add_column("% do Total", style="magenta", justify="right")
                
                for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                    percentual = (valor / total_compartilhado * 100) if total_compartilhado > 0 else 0
                    cat_table.add_row(cat, f"R$ {valor:,.2f}", f"{percentual:.1f}%")
                
                self.console.print(cat_table)
                
        except Exception as e:
            self.console.print(f"[red]Erro ao detalhar fatura: {e}[/red]")
        
        self.console.print("\n[dim]Pressione Enter para continuar...[/dim]")
        input()
    
    def _historico_compartilhado_mensal(self):
        """Exibe histórico mensal de transações compartilhadas"""
        self.console.clear()
        self.console.print(Panel("[bold magenta]📊 Histórico Mensal Compartilhado[/bold magenta]", style="magenta"))
        
        try:
            # Solicitar período
            hoje = datetime.now()
            ano = IntPrompt.ask("Ano", default=hoje.year)
            
            # Obter transações de todos os meses do ano
            historico_mensal = []
            
            for mes in range(1, 13):
                transacoes = self.client.obter_transacoes_mes(ano, mes, compartilhadas_apenas=True)
                
                if transacoes:
                    total_debitos = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DEBITO)
                    total_creditos = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.CREDITO)
                    
                    historico_mensal.append({
                        'mes': mes,
                        'total_transacoes': len(transacoes),
                        'total_debitos': total_debitos,
                        'total_creditos': total_creditos,
                        'saldo': total_creditos - total_debitos
                    })
            
            if not historico_mensal:
                self.console.print(f"[yellow]Nenhuma transação compartilhada encontrada em {ano}.[/yellow]")
            else:
                # Calcular totais do ano
                total_anual_debitos = sum(m['total_debitos'] for m in historico_mensal)
                total_anual_creditos = sum(m['total_creditos'] for m in historico_mensal)
                saldo_anual = total_anual_creditos - total_anual_debitos
                
                # Resumo anual
                self.console.print(f"[bold cyan]Resumo Anual {ano}:[/bold cyan]")
                self.console.print(f"[bold red]Total de gastos:[/bold red] R$ {total_anual_debitos:,.2f}")
                self.console.print(f"[bold green]Total de receitas:[/bold green] R$ {total_anual_creditos:,.2f}")
                self.console.print(f"[bold cyan]Saldo anual:[/bold cyan] R$ {saldo_anual:,.2f}")
                self.console.print(f"[bold magenta]Valor dividido (50%):[/bold magenta] R$ {saldo_anual/2:,.2f}")
                self.console.print()
                
                # Tabela mensal
                table = Table(show_header=True, header_style="bold magenta", title=f"Histórico Mensal - {ano}")
                table.add_column("Mês", style="cyan")
                table.add_column("Transações", style="blue", justify="center")
                table.add_column("Gastos", style="red", justify="right")
                table.add_column("Receitas", style="green", justify="right")
                table.add_column("Saldo", style="yellow", justify="right")
                table.add_column("50%", style="magenta", justify="right")
                
                meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                
                for dados in historico_mensal:
                    mes_nome = meses_nomes[dados['mes'] - 1]
                    saldo_mes = dados['saldo']
                    
                    table.add_row(
                        mes_nome,
                        str(dados['total_transacoes']),
                        f"R$ {dados['total_debitos']:,.2f}",
                        f"R$ {dados['total_creditos']:,.2f}",
                        f"R$ {saldo_mes:,.2f}",
                        f"R$ {saldo_mes/2:,.2f}"
                    )
                
                self.console.print(table)
                
        except Exception as e:
            self.console.print(f"[red]Erro ao gerar histórico: {e}[/red]")
        
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