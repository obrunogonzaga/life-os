"""
Transaction Service - Serviços relacionados a transações financeiras
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from calendar import monthrange

from ..domains.transaction_domain_data import TransactionDomainData
from utils.database_manager import DatabaseManager
from utils.finance_models import (
    Transacao, Parcelamento, TipoTransacao, StatusTransacao
)


class TransactionService:
    """
    Service para gerenciamento de transações financeiras
    Implementa a lógica de negócios para operações com transações
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.transaction_data = TransactionDomainData(db_manager)
    
    def create_transaction(self, descricao: str, valor: float, tipo: TipoTransacao,
                          data_transacao: str, categoria: Optional[str] = None,
                          conta_id: Optional[str] = None, cartao_id: Optional[str] = None,
                          parcelas: int = 1, observacoes: Optional[str] = None,
                          compartilhado_com_alzi: bool = False) -> Optional[Transacao]:
        """
        Cria uma nova transação com validações de negócio
        
        Args:
            descricao: Descrição da transação
            valor: Valor da transação
            tipo: Tipo da transação (débito/crédito)
            data_transacao: Data da transação (ISO format)
            categoria: Categoria da transação
            conta_id: ID da conta associada
            cartao_id: ID do cartão associado
            parcelas: Número de parcelas (padrão 1)
            observacoes: Observações adicionais
            compartilhado_com_alzi: Se a transação é compartilhada com Alzi
            
        Returns:
            Transacao criada ou None em caso de erro
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
        """
        # Validações de negócio
        if not descricao or not descricao.strip():
            raise ValueError("Descrição da transação é obrigatória")
        
        if valor <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        if not data_transacao:
            raise ValueError("Data da transação é obrigatória")
        
        # Validar formato da data
        try:
            datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Formato de data inválido. Use formato ISO (YYYY-MM-DD)")
        
        # Deve ter conta ou cartão, mas não ambos
        if not conta_id and not cartao_id:
            raise ValueError("Deve ser informada uma conta ou um cartão")
        
        if conta_id and cartao_id:
            raise ValueError("Não é possível associar a transação a conta e cartão simultaneamente")
        
        if parcelas < 1:
            raise ValueError("Número de parcelas deve ser maior que zero")
        
        # Para cartão de crédito, apenas débitos podem ser parcelados
        if cartao_id and parcelas > 1 and tipo != TipoTransacao.DEBITO:
            raise ValueError("Apenas débitos podem ser parcelados em cartão de crédito")
        
        # Verificar se conta/cartão existem
        if conta_id:
            from .account_service import AccountService
            account_service = AccountService(self.db_manager)
            if not account_service.get_account_by_id(conta_id):
                raise ValueError("Conta não encontrada")
        
        if cartao_id:
            from .card_service import CardService
            card_service = CardService(self.db_manager)
            if not card_service.get_card_by_id(cartao_id):
                raise ValueError("Cartão não encontrado")
        
        # Gerar parcelamento se necessário
        parcelamento = self._generate_installments(valor, parcelas, data_transacao)
        
        # Criar a transação
        transaction = self.transaction_data.create_transaction(
            descricao=descricao.strip(),
            valor=valor,
            tipo=tipo,
            data_transacao=data_transacao,
            categoria=categoria,
            conta_id=conta_id,
            cartao_id=cartao_id,
            parcelamento=parcelamento,
            observacoes=observacoes,
            compartilhado_com_alzi=compartilhado_com_alzi
        )
        
        if transaction:
            # Atualizar saldo da conta ou limite do cartão
            self._update_balance_or_limit(transaction)
        
        return transaction
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transacao]:
        """
        Obtém uma transação pelo ID
        
        Args:
            transaction_id: ID da transação
            
        Returns:
            Transacao ou None se não encontrada
        """
        if not transaction_id:
            return None
        
        return self.transaction_data.get_transaction_by_id(transaction_id)
    
    def list_transactions(self, filters: Optional[Dict[str, Any]] = None) -> List[Transacao]:
        """
        Lista transações com filtros opcionais
        
        Args:
            filters: Dicionário com filtros a serem aplicados
            
        Returns:
            Lista de transações que atendem aos critérios
        """
        return self.transaction_data.list_transactions(filters or {})
    
    def get_transactions_by_month(self, ano: int, mes: int, 
                                 shared_only: bool = False) -> List[Transacao]:
        """
        Obtém transações de um mês específico
        
        Args:
            ano: Ano
            mes: Mês (1-12)
            shared_only: Se deve retornar apenas transações compartilhadas
            
        Returns:
            Lista de transações do mês
        """
        # Validações
        if not (1 <= mes <= 12):
            raise ValueError("Mês deve estar entre 1 e 12")
        
        if ano < 1900 or ano > 2100:
            raise ValueError("Ano deve estar entre 1900 e 2100")
        
        data_inicio = f"{ano}-{mes:02d}-01"
        if mes == 12:
            data_fim = f"{ano + 1}-01-01"
        else:
            data_fim = f"{ano}-{mes + 1:02d}-01"
        
        filters = {
            "data_transacao": {"$gte": data_inicio, "$lt": data_fim}
        }
        
        if shared_only:
            filters["compartilhado_com_alzi"] = True
        
        return self.list_transactions(filters)
    
    def update_transaction(self, transaction_id: str, **kwargs) -> bool:
        """
        Atualiza uma transação com validações
        
        Args:
            transaction_id: ID da transação a ser atualizada
            **kwargs: Campos a serem atualizados
            
        Returns:
            True se a atualização foi bem-sucedida
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
        """
        if not transaction_id:
            raise ValueError("ID da transação é obrigatório")
        
        # Verificar se a transação existe
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transação não encontrada")
        
        # Validações para campos específicos
        if 'descricao' in kwargs and (not kwargs['descricao'] or not kwargs['descricao'].strip()):
            raise ValueError("Descrição da transação não pode ser vazia")
        
        if 'valor' in kwargs and kwargs['valor'] <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        if 'data_transacao' in kwargs:
            try:
                datetime.fromisoformat(kwargs['data_transacao'].replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Formato de data inválido")
        
        # Se mudou valor ou tipo, atualizar saldos/limites
        valor_mudou = 'valor' in kwargs and kwargs['valor'] != transaction.valor
        tipo_mudou = 'tipo' in kwargs and kwargs['tipo'] != transaction.tipo
        
        if valor_mudou or tipo_mudou:
            # Reverter operação anterior
            self._revert_balance_or_limit(transaction)
            
            # Aplicar nova operação
            updated_transaction = Transacao(
                id=transaction.id,
                descricao=kwargs.get('descricao', transaction.descricao),
                valor=kwargs.get('valor', transaction.valor),
                tipo=kwargs.get('tipo', transaction.tipo),
                data_transacao=kwargs.get('data_transacao', transaction.data_transacao),
                categoria=kwargs.get('categoria', transaction.categoria),
                conta_id=transaction.conta_id,
                cartao_id=transaction.cartao_id,
                parcelamento=transaction.parcelamento,
                observacoes=kwargs.get('observacoes', transaction.observacoes),
                status=transaction.status,
                compartilhado_com_alzi=kwargs.get('compartilhado_com_alzi', transaction.compartilhado_com_alzi),
                created_at=transaction.created_at,
                updated_at=datetime.now().isoformat()
            )
            self._update_balance_or_limit(updated_transaction)
        
        return self.transaction_data.update_transaction(transaction_id, **kwargs)
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """
        Exclui uma transação e reverte os ajustes de saldo/limite
        
        Args:
            transaction_id: ID da transação a ser excluída
            
        Returns:
            True se a exclusão foi bem-sucedida
        """
        if not transaction_id:
            raise ValueError("ID da transação é obrigatório")
        
        # Obter a transação antes de deletar
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transação não encontrada")
        
        # Deletar a transação
        success = self.transaction_data.delete_transaction(transaction_id)
        
        if success:
            # Reverter ajustes de saldo/limite
            self._revert_balance_or_limit(transaction)
        
        return success
    
    def delete_multiple_transactions(self, transaction_ids: List[str]) -> Dict[str, Any]:
        """
        Exclui múltiplas transações
        
        Args:
            transaction_ids: Lista de IDs das transações
            
        Returns:
            Dicionário com resultado da operação
        """
        result = {
            'success': True,
            'total_requested': len(transaction_ids),
            'deleted': 0,
            'errors': []
        }
        
        for transaction_id in transaction_ids:
            try:
                if self.delete_transaction(transaction_id):
                    result['deleted'] += 1
                else:
                    result['errors'].append(f"Falha ao excluir transação {transaction_id[:8]}...")
            except Exception as e:
                result['errors'].append(f"Erro ao excluir {transaction_id[:8]}...: {e}")
        
        if result['errors']:
            result['success'] = False
        
        return result
    
    def get_transactions_summary(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retorna um resumo das transações com estatísticas
        
        Args:
            filters: Filtros opcionais
            
        Returns:
            Dicionário com estatísticas das transações
        """
        transactions = self.list_transactions(filters)
        
        total_debitos = sum(t.valor for t in transactions if t.tipo == TipoTransacao.DEBITO)
        total_creditos = sum(t.valor for t in transactions if t.tipo == TipoTransacao.CREDITO)
        total_compartilhado = sum(t.valor for t in transactions 
                                if t.compartilhado_com_alzi and t.tipo == TipoTransacao.DEBITO)
        
        return {
            'total_transactions': len(transactions),
            'total_debits': total_debitos,
            'total_credits': total_creditos,
            'balance': total_creditos - total_debitos,
            'shared_expenses': total_compartilhado,
            'transactions_by_category': self._group_by_category(transactions),
            'transactions_by_type': self._group_by_type(transactions)
        }
    
    def _generate_installments(self, valor: float, parcelas: int, data_base: str) -> List[Parcelamento]:
        """
        Gera lista de parcelamentos
        
        Args:
            valor: Valor total
            parcelas: Número de parcelas
            data_base: Data base para cálculo
            
        Returns:
            Lista de parcelamentos
        """
        if parcelas <= 1:
            return []
        
        parcelamento = []
        valor_parcela = valor / parcelas
        data_dt = datetime.fromisoformat(data_base.replace('Z', '+00:00'))
        
        for i in range(parcelas):
            # Calcular data de vencimento (mês + i)
            mes = data_dt.month + i
            ano = data_dt.year
            while mes > 12:
                mes -= 12
                ano += 1
            
            # Último dia do mês se o dia não existir
            ultimo_dia = monthrange(ano, mes)[1]
            dia = min(data_dt.day, ultimo_dia)
            
            data_vencimento = datetime(ano, mes, dia).isoformat()
            
            parcela = Parcelamento(
                numero_parcela=i + 1,
                total_parcelas=parcelas,
                valor_parcela=valor_parcela,
                data_vencimento=data_vencimento
            )
            parcelamento.append(parcela)
        
        return parcelamento
    
    def _update_balance_or_limit(self, transaction: Transacao):
        """
        Atualiza saldo da conta ou limite do cartão baseado na transação
        
        Args:
            transaction: Transação para processar
        """
        if transaction.conta_id:
            from .account_service import AccountService
            account_service = AccountService(self.db_manager)
            account_service.update_balance(transaction.conta_id, transaction.valor, transaction.tipo)
        
        elif transaction.cartao_id:
            from .card_service import CardService
            card_service = CardService(self.db_manager)
            # Para cartão, sempre diminui o limite disponível (mesmo para créditos)
            if transaction.tipo == TipoTransacao.DEBITO:
                card_service.update_available_limit(transaction.cartao_id, transaction.valor, 'decrease')
            else:
                # Crédito em cartão (pagamento) aumenta o limite disponível
                card_service.update_available_limit(transaction.cartao_id, transaction.valor, 'increase')
    
    def _revert_balance_or_limit(self, transaction: Transacao):
        """
        Reverte os ajustes de saldo/limite de uma transação
        
        Args:
            transaction: Transação a ser revertida
        """
        if transaction.conta_id:
            from .account_service import AccountService
            account_service = AccountService(self.db_manager)
            # Inverter o tipo da transação para reverter
            tipo_reverso = TipoTransacao.CREDITO if transaction.tipo == TipoTransacao.DEBITO else TipoTransacao.DEBITO
            account_service.update_balance(transaction.conta_id, transaction.valor, tipo_reverso)
        
        elif transaction.cartao_id:
            from .card_service import CardService
            card_service = CardService(self.db_manager)
            # Para cartão, inverter a operação
            if transaction.tipo == TipoTransacao.DEBITO:
                card_service.update_available_limit(transaction.cartao_id, transaction.valor, 'increase')
            else:
                card_service.update_available_limit(transaction.cartao_id, transaction.valor, 'decrease')
    
    def _group_by_category(self, transactions: List[Transacao]) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa transações por categoria
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Dicionário com estatísticas por categoria
        """
        grouped = {}
        
        for transaction in transactions:
            categoria = transaction.categoria or 'Sem categoria'
            
            if categoria not in grouped:
                grouped[categoria] = {
                    'count': 0,
                    'total_debits': 0.0,
                    'total_credits': 0.0
                }
            
            grouped[categoria]['count'] += 1
            
            if transaction.tipo == TipoTransacao.DEBITO:
                grouped[categoria]['total_debits'] += transaction.valor
            else:
                grouped[categoria]['total_credits'] += transaction.valor
        
        return grouped
    
    def _group_by_type(self, transactions: List[Transacao]) -> Dict[str, int]:
        """
        Agrupa transações por tipo
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Dicionário com contagem por tipo
        """
        grouped = {}
        
        for transaction in transactions:
            tipo = transaction.tipo.value if hasattr(transaction.tipo, 'value') else str(transaction.tipo)
            grouped[tipo] = grouped.get(tipo, 0) + 1
        
        return grouped