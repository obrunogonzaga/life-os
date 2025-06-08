"""
Account Service - Serviços relacionados a contas correntes
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domains.account_domain import AccountDomain
from ..domains.account_domain_data import AccountDomainData
from utils.database_manager import DatabaseManager
from utils.finance_models import ContaCorrente, TipoConta, TipoTransacao


class AccountService:
    """
    Service para gerenciamento de contas correntes
    Implementa a lógica de negócios para operações com contas
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.account_data = AccountDomainData(db_manager)
    
    def create_account(self, nome: str, banco: str, agencia: str, conta: str, 
                      tipo: TipoConta, saldo_inicial: float, 
                      compartilhado_com_alzi: bool = False) -> Optional[ContaCorrente]:
        """
        Cria uma nova conta corrente com validações de negócio
        
        Args:
            nome: Nome identificador da conta
            banco: Nome do banco
            agencia: Número da agência
            conta: Número da conta
            tipo: Tipo da conta (corrente, poupança, investimento)
            saldo_inicial: Saldo inicial da conta
            compartilhado_com_alzi: Se a conta é compartilhada com Alzi
            
        Returns:
            ContaCorrente criada ou None em caso de erro
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
        """
        # Validações de negócio
        if not nome or not nome.strip():
            raise ValueError("Nome da conta é obrigatório")
        
        if not banco or not banco.strip():
            raise ValueError("Nome do banco é obrigatório")
        
        if not agencia or not agencia.strip():
            raise ValueError("Número da agência é obrigatório")
        
        if not conta or not conta.strip():
            raise ValueError("Número da conta é obrigatório")
        
        if saldo_inicial < 0:
            raise ValueError("Saldo inicial não pode ser negativo")
        
        # Verificar se já existe conta com mesma agência/conta no mesmo banco
        if self._account_exists(banco, agencia, conta):
            raise ValueError(f"Já existe uma conta {agencia}/{conta} no banco {banco}")
        
        return self.account_data.create_account(
            nome=nome.strip(),
            banco=banco.strip(),
            agencia=agencia.strip(),
            conta=conta.strip(),
            tipo=tipo,
            saldo_inicial=saldo_inicial,
            compartilhado_com_alzi=compartilhado_com_alzi
        )
    
    def get_account_by_id(self, account_id: str) -> Optional[ContaCorrente]:
        """
        Obtém uma conta pelo ID
        
        Args:
            account_id: ID da conta
            
        Returns:
            ContaCorrente ou None se não encontrada
        """
        if not account_id:
            return None
        
        return self.account_data.get_account_by_id(account_id)
    
    def list_accounts(self, active_only: bool = True, 
                     shared_with_alzi_only: bool = False) -> List[ContaCorrente]:
        """
        Lista contas com filtros opcionais
        
        Args:
            active_only: Se deve listar apenas contas ativas
            shared_with_alzi_only: Se deve listar apenas contas compartilhadas com Alzi
            
        Returns:
            Lista de contas que atendem aos critérios
        """
        accounts = self.account_data.list_accounts(active_only)
        
        if shared_with_alzi_only:
            accounts = [acc for acc in accounts if acc.compartilhado_com_alzi]
        
        return accounts
    
    def update_account(self, account_id: str, **kwargs) -> bool:
        """
        Atualiza dados de uma conta com validações
        
        Args:
            account_id: ID da conta a ser atualizada
            **kwargs: Campos a serem atualizados
            
        Returns:
            True se a atualização foi bem-sucedida
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
        """
        if not account_id:
            raise ValueError("ID da conta é obrigatório")
        
        # Verificar se a conta existe
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError("Conta não encontrada")
        
        # Validações específicas para campos que podem ser atualizados
        if 'nome' in kwargs and (not kwargs['nome'] or not kwargs['nome'].strip()):
            raise ValueError("Nome da conta não pode ser vazio")
        
        if 'banco' in kwargs and (not kwargs['banco'] or not kwargs['banco'].strip()):
            raise ValueError("Nome do banco não pode ser vazio")
        
        if 'saldo_atual' in kwargs and kwargs['saldo_atual'] < 0:
            raise ValueError("Saldo atual não pode ser negativo")
        
        # Verificar duplicação de conta se agência/conta estão sendo alteradas
        if 'agencia' in kwargs or 'conta' in kwargs:
            new_agencia = kwargs.get('agencia', account.agencia)
            new_conta = kwargs.get('conta', account.conta)
            new_banco = kwargs.get('banco', account.banco)
            
            if self._account_exists(new_banco, new_agencia, new_conta, exclude_id=account_id):
                raise ValueError(f"Já existe uma conta {new_agencia}/{new_conta} no banco {new_banco}")
        
        return self.account_data.update_account(account_id, **kwargs)
    
    def deactivate_account(self, account_id: str) -> bool:
        """
        Desativa uma conta (soft delete)
        
        Args:
            account_id: ID da conta a ser desativada
            
        Returns:
            True se a desativação foi bem-sucedida
        """
        if not account_id:
            raise ValueError("ID da conta é obrigatório")
        
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError("Conta não encontrada")
        
        return self.account_data.update_account(account_id, ativa=False)
    
    def activate_account(self, account_id: str) -> bool:
        """
        Reativa uma conta desativada
        
        Args:
            account_id: ID da conta a ser reativada
            
        Returns:
            True se a reativação foi bem-sucedida
        """
        if not account_id:
            raise ValueError("ID da conta é obrigatório")
        
        return self.account_data.update_account(account_id, ativa=True)
    
    def update_balance(self, account_id: str, valor: float, tipo: TipoTransacao) -> bool:
        """
        Atualiza o saldo de uma conta baseado em uma transação
        
        Args:
            account_id: ID da conta
            valor: Valor da transação
            tipo: Tipo da transação (débito/crédito)
            
        Returns:
            True se a atualização foi bem-sucedida
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
        """
        if not account_id:
            raise ValueError("ID da conta é obrigatório")
        
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
        
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError("Conta não encontrada")
        
        # Calcular novo saldo
        if tipo == TipoTransacao.DEBITO:
            novo_saldo = account.saldo_atual - valor
        else:  # CREDITO
            novo_saldo = account.saldo_atual + valor
        
        # Permitir saldo negativo (para descoberto)
        return self.account_data.update_account(account_id, saldo_atual=novo_saldo)
    
    def get_total_balance(self, active_only: bool = True) -> float:
        """
        Calcula o saldo total de todas as contas
        
        Args:
            active_only: Se deve considerar apenas contas ativas
            
        Returns:
            Saldo total das contas
        """
        accounts = self.list_accounts(active_only=active_only)
        return sum(acc.saldo_atual for acc in accounts)
    
    def get_shared_accounts_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo das contas compartilhadas com Alzi
        
        Returns:
            Dicionário com estatísticas das contas compartilhadas
        """
        shared_accounts = self.list_accounts(shared_with_alzi_only=True)
        
        return {
            'total_accounts': len(shared_accounts),
            'total_balance': sum(acc.saldo_atual for acc in shared_accounts),
            'accounts_by_type': self._group_accounts_by_type(shared_accounts),
            'accounts': shared_accounts
        }
    
    def _account_exists(self, banco: str, agencia: str, conta: str, 
                       exclude_id: Optional[str] = None) -> bool:
        """
        Verifica se já existe uma conta com os mesmos dados
        
        Args:
            banco: Nome do banco
            agencia: Número da agência
            conta: Número da conta
            exclude_id: ID de conta a ser excluído da verificação
            
        Returns:
            True se a conta já existe
        """
        accounts = self.account_data.list_accounts(active_only=False)
        
        for acc in accounts:
            if (acc.banco.lower() == banco.lower() and 
                acc.agencia == agencia and 
                acc.conta == conta and
                acc.id != exclude_id):
                return True
        
        return False
    
    def _group_accounts_by_type(self, accounts: List[ContaCorrente]) -> Dict[str, int]:
        """
        Agrupa contas por tipo
        
        Args:
            accounts: Lista de contas
            
        Returns:
            Dicionário com contagem por tipo
        """
        grouped = {}
        for acc in accounts:
            tipo = acc.tipo.value if hasattr(acc.tipo, 'value') else str(acc.tipo)
            grouped[tipo] = grouped.get(tipo, 0) + 1
        
        return grouped