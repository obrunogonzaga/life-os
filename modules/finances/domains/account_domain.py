"""
Domínio de Contas - Regras de Negócio

Esta classe contém todas as regras de negócio relacionadas a contas correntes,
poupança e investimento, sem dependências de infraestrutura ou interface.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid

from utils.finance_models import ContaCorrente, TipoConta, TipoTransacao


class AccountDomain:
    """
    Domínio responsável pelas regras de negócio de contas
    """

    @staticmethod
    def validate_account_data(
        nome: str,
        banco: str, 
        agencia: str,
        conta: str,
        tipo: TipoConta,
        saldo_inicial: float
    ) -> Dict[str, Any]:
        """
        Valida dados de conta e retorna resultado da validação
        
        Returns:
            Dict com 'valid': bool e 'errors': List[str]
        """
        errors = []
        
        # Validar nome
        if not nome or len(nome.strip()) < 2:
            errors.append("Nome da conta deve ter pelo menos 2 caracteres")
        
        # Validar banco
        if not banco or len(banco.strip()) < 2:
            errors.append("Nome do banco deve ter pelo menos 2 caracteres")
            
        # Validar agência
        if not agencia or len(agencia.strip()) < 3:
            errors.append("Agência deve ter pelo menos 3 caracteres")
            
        # Validar conta
        if not conta or len(conta.strip()) < 4:
            errors.append("Número da conta deve ter pelo menos 4 caracteres")
            
        # Validar tipo
        if not isinstance(tipo, TipoConta):
            errors.append("Tipo de conta inválido")
            
        # Validar saldo inicial
        if saldo_inicial < 0 and tipo != TipoConta.CORRENTE:
            errors.append("Saldo inicial não pode ser negativo para poupança e investimento")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def calculate_new_balance(
        current_balance: float,
        transaction_value: float,
        transaction_type: TipoTransacao
    ) -> float:
        """
        Calcula novo saldo após transação
        
        Args:
            current_balance: Saldo atual da conta
            transaction_value: Valor da transação  
            transaction_type: Tipo da transação (DEBITO/CREDITO)
            
        Returns:
            Novo saldo calculado
        """
        # Usar Decimal para precisão monetária
        current = Decimal(str(current_balance))
        value = Decimal(str(transaction_value))
        
        if transaction_type == TipoTransacao.DEBITO:
            new_balance = current - value
        else:  # CREDITO
            new_balance = current + value
            
        # Retornar como float com 2 casas decimais
        return float(new_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def can_account_be_deleted(account: ContaCorrente, has_transactions: bool) -> Dict[str, Any]:
        """
        Verifica se uma conta pode ser excluída
        
        Args:
            account: Conta a ser verificada
            has_transactions: Se a conta possui transações
            
        Returns:
            Dict com 'can_delete': bool e 'reason': str
        """
        if has_transactions:
            return {
                'can_delete': False,
                'reason': 'Conta possui transações. Use inativação ao invés de exclusão.'
            }
            
        if account.saldo_atual != 0:
            return {
                'can_delete': False, 
                'reason': 'Conta deve ter saldo zero para ser excluída.'
            }
            
        return {
            'can_delete': True,
            'reason': ''
        }

    @staticmethod
    def calculate_accounts_summary(accounts: List[ContaCorrente]) -> Dict[str, Any]:
        """
        Calcula resumo financeiro das contas
        
        Args:
            accounts: Lista de contas
            
        Returns:
            Dict com estatísticas das contas
        """
        active_accounts = [acc for acc in accounts if acc.ativa]
        
        total_balance = sum(
            Decimal(str(acc.saldo_atual)) for acc in active_accounts
        )
        
        shared_accounts = [acc for acc in active_accounts if acc.compartilhado_com_alzi]
        
        # Saldo por tipo de conta
        balance_by_type = {}
        for tipo in TipoConta:
            type_accounts = [acc for acc in active_accounts if acc.tipo == tipo]
            type_balance = sum(Decimal(str(acc.saldo_atual)) for acc in type_accounts) if type_accounts else Decimal('0')
            balance_by_type[tipo.value] = float(
                type_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
        
        return {
            'total_accounts': len(active_accounts),
            'total_balance': float(total_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'shared_accounts_count': len(shared_accounts),
            'shared_accounts_balance': float(
                sum(Decimal(str(acc.saldo_atual)) for acc in shared_accounts)
                .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            ),
            'balance_by_type': balance_by_type,
            'inactive_accounts': len(accounts) - len(active_accounts)
        }

    @staticmethod
    def generate_account_id() -> str:
        """
        Gera ID único para nova conta
        
        Returns:
            ID único da conta
        """
        return str(uuid.uuid4())

    @staticmethod
    def prepare_account_creation_data(
        nome: str,
        banco: str,
        agencia: str, 
        conta: str,
        tipo: TipoConta,
        saldo_inicial: float,
        compartilhado_com_alzi: bool = False
    ) -> Dict[str, Any]:
        """
        Prepara dados para criação de conta com regras de negócio aplicadas
        
        Returns:
            Dict com dados preparados para criação
        """
        now = datetime.now().isoformat()
        
        return {
            'id': AccountDomain.generate_account_id(),
            'nome': nome.strip(),
            'banco': banco.strip(),
            'agencia': agencia.strip(),
            'conta': conta.strip(),
            'tipo': tipo,
            'saldo_inicial': saldo_inicial,
            'saldo_atual': saldo_inicial,  # Regra: saldo atual = inicial na criação
            'compartilhado_com_alzi': compartilhado_com_alzi,
            'ativa': True,  # Regra: conta sempre inicia ativa
            'created_at': now,
            'updated_at': now
        }

    @staticmethod
    def prepare_account_update_data(
        current_account: ContaCorrente,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepara dados para atualização de conta aplicando regras de negócio
        
        Args:
            current_account: Conta atual
            **kwargs: Campos a serem atualizados
            
        Returns:
            Dict com dados preparados para atualização
        """
        # Campos que podem ser atualizados
        updatable_fields = {
            'nome', 'banco', 'agencia', 'conta', 'tipo',
            'saldo_inicial', 'saldo_atual', 'compartilhado_com_alzi', 'ativa'
        }
        
        update_data = {}
        
        for field, value in kwargs.items():
            if field in updatable_fields and value is not None:
                update_data[field] = value
                
        # Sempre atualizar timestamp
        update_data['updated_at'] = datetime.now().isoformat()
        
        return update_data

    @staticmethod
    def filter_accounts_by_criteria(
        accounts: List[ContaCorrente],
        ativas_apenas: bool = True,
        compartilhadas_apenas: Optional[bool] = None,
        tipo: Optional[TipoConta] = None
    ) -> List[ContaCorrente]:
        """
        Filtra contas por critérios específicos
        
        Args:
            accounts: Lista de contas
            ativas_apenas: Filtrar apenas contas ativas
            compartilhadas_apenas: Filtrar apenas compartilhadas (None = todas)
            tipo: Filtrar por tipo de conta (None = todos os tipos)
            
        Returns:
            Lista filtrada de contas
        """
        filtered = accounts
        
        if ativas_apenas:
            filtered = [acc for acc in filtered if acc.ativa]
            
        if compartilhadas_apenas is not None:
            filtered = [acc for acc in filtered 
                       if acc.compartilhado_com_alzi == compartilhadas_apenas]
            
        if tipo is not None:
            filtered = [acc for acc in filtered if acc.tipo == tipo]
            
        return filtered

    @staticmethod
    def is_account_balance_valid_for_transaction(
        account: ContaCorrente,
        transaction_value: float,
        transaction_type: TipoTransacao
    ) -> Dict[str, Any]:
        """
        Verifica se o saldo da conta permite a transação
        
        Args:
            account: Conta a ser verificada
            transaction_value: Valor da transação
            transaction_type: Tipo da transação
            
        Returns:
            Dict com 'valid': bool e 'message': str
        """
        if transaction_type == TipoTransacao.CREDITO:
            return {'valid': True, 'message': ''}
            
        # Para débito, verificar saldo
        new_balance = AccountDomain.calculate_new_balance(
            account.saldo_atual, transaction_value, transaction_type
        )
        
        # Conta corrente pode ficar negativa, outras não
        if account.tipo != TipoConta.CORRENTE and new_balance < 0:
            return {
                'valid': False,
                'message': f'Saldo insuficiente. Saldo atual: R$ {account.saldo_atual:.2f}'
            }
            
        return {'valid': True, 'message': ''}