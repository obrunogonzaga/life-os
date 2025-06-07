"""
Domínio de Transações - Regras de Negócio

Esta classe contém todas as regras de negócio relacionadas a transações,
incluindo parcelamento, cálculos de saldo, períodos de fatura e validações.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
import uuid
from calendar import monthrange

from utils.finance_models import (
    Transacao, Parcelamento, TipoTransacao, StatusTransacao,
    ContaCorrente, CartaoCredito
)


class TransactionDomain:
    """
    Domínio responsável pelas regras de negócio de transações
    """

    @staticmethod
    def validate_transaction_data(
        descricao: str,
        valor: float,
        tipo: TipoTransacao,
        data_transacao: str,
        conta_id: Optional[str] = None,
        cartao_id: Optional[str] = None,
        parcelas: int = 1
    ) -> Dict[str, Any]:
        """
        Valida dados de transação
        
        Returns:
            Dict com 'valid': bool e 'errors': List[str]
        """
        errors = []
        
        # Validar descrição
        if not descricao or len(descricao.strip()) < 2:
            errors.append("Descrição deve ter pelo menos 2 caracteres")
        
        # Validar valor
        if valor <= 0:
            errors.append("Valor deve ser maior que zero")
            
        # Validar tipo
        if not isinstance(tipo, TipoTransacao):
            errors.append("Tipo de transação inválido")
            
        # Validar data
        try:
            datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
        except ValueError:
            errors.append("Data de transação inválida")
            
        # Validar origem (conta ou cartão)
        if not conta_id and not cartao_id:
            errors.append("Transação deve ter uma conta ou cartão vinculado")
            
        if conta_id and cartao_id:
            errors.append("Transação não pode ter conta e cartão vinculados simultaneamente")
            
        # Validar parcelas para cartão
        if cartao_id and parcelas > 1 and tipo != TipoTransacao.DEBITO:
            errors.append("Parcelamento só é permitido para débitos (compras) em cartão")
            
        if parcelas < 1 or parcelas > 60:  # Limite razoável
            errors.append("Número de parcelas deve estar entre 1 e 60")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def calculate_installments(
        valor: float,
        parcelas: int,
        data_transacao: str
    ) -> List[Parcelamento]:
        """
        Calcula parcelamento de uma transação
        
        Args:
            valor: Valor total da transação
            parcelas: Número de parcelas
            data_transacao: Data da transação (ISO format)
            
        Returns:
            Lista de objetos Parcelamento
        """
        if parcelas <= 1:
            return []
            
        parcelamento = []
        valor_parcela = Decimal(str(valor)) / Decimal(str(parcelas))
        # Arredondar para 2 casas decimais
        valor_parcela = valor_parcela.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        data_base = datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
        
        for i in range(parcelas):
            # Calcular data de vencimento (mês + i)
            mes = data_base.month + i
            ano = data_base.year
            
            # Ajustar ano se mês exceder 12
            while mes > 12:
                mes -= 12
                ano += 1
            
            # Ajustar dia se não existir no mês de destino
            ultimo_dia = monthrange(ano, mes)[1]
            dia = min(data_base.day, ultimo_dia)
            
            data_vencimento = datetime(ano, mes, dia).isoformat()
            
            # Ajustar valor da última parcela para compensar arredondamentos
            if i == parcelas - 1:
                # Recalcular para evitar diferenças de centavos
                valor_usado = valor_parcela * (parcelas - 1)
                valor_ultima = Decimal(str(valor)) - valor_usado
                valor_parcela_final = valor_ultima
            else:
                valor_parcela_final = valor_parcela
            
            parcela = Parcelamento(
                numero_parcela=i + 1,
                total_parcelas=parcelas,
                valor_parcela=float(valor_parcela_final),
                data_vencimento=data_vencimento,
                pago=False
            )
            parcelamento.append(parcela)
            
        return parcelamento

    @staticmethod
    def calculate_invoice_month_for_transaction(
        transaction_date: date,
        closing_day: int
    ) -> Tuple[int, int]:
        """
        Determina em qual mês/ano de fatura uma transação deve aparecer
        
        Args:
            transaction_date: Data da transação
            closing_day: Dia de fechamento do cartão
            
        Returns:
            Tupla com (mês, ano) da fatura onde a transação aparece
        """
        # Ajustar dia de fechamento para o mês da transação
        month_days = monthrange(transaction_date.year, transaction_date.month)[1]
        adjusted_closing_day = min(closing_day, month_days)
        
        if transaction_date.day > adjusted_closing_day:
            # Transação após fechamento vai para fatura que vence em 2 meses
            if transaction_date.month >= 11:  # Novembro ou Dezembro
                mes_fatura = transaction_date.month - 10  # 11->1, 12->2
                ano_fatura = transaction_date.year + 1
            else:
                mes_fatura = transaction_date.month + 2
                ano_fatura = transaction_date.year
        else:
            # Transação até fechamento vai para fatura do próximo mês
            if transaction_date.month == 12:
                mes_fatura = 1
                ano_fatura = transaction_date.year + 1
            else:
                mes_fatura = transaction_date.month + 1
                ano_fatura = transaction_date.year
                
        return mes_fatura, ano_fatura

    @staticmethod
    def calculate_invoice_period_for_card(
        closing_day: int,
        invoice_month: int,
        invoice_year: int
    ) -> Tuple[date, date]:
        """
        Calcula período de transações para uma fatura específica
        
        Args:
            closing_day: Dia de fechamento do cartão
            invoice_month: Mês da fatura (vencimento)
            invoice_year: Ano da fatura (vencimento)
            
        Returns:
            Tupla com (data_inicio, data_fim) do período das transações
        """
        # IMPORTANTE: Fatura com vencimento em MÊS X contém transações do mês ANTERIOR
        # Para fatura de mês X, pegar transações do mês X-1
        if invoice_month == 1:
            transaction_month = 12
            transaction_year = invoice_year - 1
        else:
            transaction_month = invoice_month - 1
            transaction_year = invoice_year
            
        # Data de início: dia seguinte ao fechamento do mês anterior
        if transaction_month == 1:
            prev_month = 12
            prev_year = transaction_year - 1
        else:
            prev_month = transaction_month - 1
            prev_year = transaction_year
            
        # Ajustar dia de fechamento se não existir no mês anterior
        prev_month_days = monthrange(prev_year, prev_month)[1]
        adjusted_prev_closing = min(closing_day, prev_month_days)
        
        start_date = date(prev_year, prev_month, adjusted_prev_closing)
        
        # Data de fim: dia de fechamento do mês das transações
        transaction_month_days = monthrange(transaction_year, transaction_month)[1]
        adjusted_closing = min(closing_day, transaction_month_days)
        
        end_date = date(transaction_year, transaction_month, adjusted_closing)
        
        return start_date, end_date

    @staticmethod
    def is_duplicate_transaction(
        existing_transactions: List[Transacao],
        new_transaction_data: Dict[str, Any],
        tolerance_cents: float = 0.01
    ) -> bool:
        """
        Verifica se uma transação é duplicata
        
        Args:
            existing_transactions: Lista de transações existentes
            new_transaction_data: Dados da nova transação
            tolerance_cents: Tolerância para diferença de valor (centavos)
            
        Returns:
            True se for duplicata
        """
        new_date = new_transaction_data.get('data_transacao', '')[:10]  # YYYY-MM-DD
        new_value = new_transaction_data.get('valor', 0)
        new_account_id = new_transaction_data.get('conta_id')
        new_card_id = new_transaction_data.get('cartao_id')
        
        for transaction in existing_transactions:
            # Verificar data
            if transaction.data_transacao[:10] != new_date:
                continue
                
            # Verificar origem (conta ou cartão)
            if transaction.conta_id != new_account_id or transaction.cartao_id != new_card_id:
                continue
                
            # Verificar valor com tolerância
            if abs(transaction.valor - new_value) < tolerance_cents:
                return True
                
        return False

    @staticmethod
    def should_ignore_transaction_description(
        descricao: str
    ) -> bool:
        """
        Verifica se uma transação deve ser ignorada baseada na descrição
        
        Args:
            descricao: Descrição da transação
            
        Returns:
            True se deve ser ignorada
        """
        descricoes_ignorar = [
            'SALDO ANTERIOR',
            'PAGTO. POR DEB EM C/C',
            'PAGAMENTO',
            'ESTORNO',
            'JUROS',
            'MULTA',
            'ANUIDADE',
            'REND POUP',
            'RENDIMENTO',
            'IOF',
            'TARIFA'
        ]
        
        descricao_upper = descricao.upper()
        return any(termo in descricao_upper for termo in descricoes_ignorar)

    @staticmethod
    def calculate_reversal_transaction_type(
        original_type: TipoTransacao
    ) -> TipoTransacao:
        """
        Calcula tipo de transação para reverter uma operação
        
        Args:
            original_type: Tipo original da transação
            
        Returns:
            Tipo reverso para desfazer o efeito
        """
        return TipoTransacao.CREDITO if original_type == TipoTransacao.DEBITO else TipoTransacao.DEBITO

    @staticmethod
    def filter_transactions_by_period(
        transactions: List[Transacao],
        year: int,
        month: int
    ) -> List[Transacao]:
        """
        Filtra transações por período específico
        
        Args:
            transactions: Lista de transações
            year: Ano
            month: Mês
            
        Returns:
            Transações filtradas do período
        """
        data_inicio = f"{year}-{month:02d}-01"
        
        if month == 12:
            data_fim = f"{year + 1}-01-01"
        else:
            data_fim = f"{year}-{month + 1:02d}-01"
            
        filtered = []
        for transaction in transactions:
            if data_inicio <= transaction.data_transacao[:10] < data_fim:
                filtered.append(transaction)
                
        return filtered

    @staticmethod
    def generate_transaction_id() -> str:
        """Gera ID único para nova transação"""
        return str(uuid.uuid4())

    @staticmethod
    def prepare_transaction_creation_data(
        descricao: str,
        valor: float,
        tipo: TipoTransacao,
        data_transacao: str,
        categoria: Optional[str] = None,
        conta_id: Optional[str] = None,
        cartao_id: Optional[str] = None,
        parcelas: int = 1,
        observacoes: Optional[str] = None,
        compartilhado_com_alzi: bool = False
    ) -> Dict[str, Any]:
        """
        Prepara dados para criação de transação com regras de negócio aplicadas
        
        Returns:
            Dict com dados preparados para criação
        """
        now = datetime.now().isoformat()
        
        # Calcular parcelamento se necessário
        parcelamento = TransactionDomain.calculate_installments(
            valor, parcelas, data_transacao
        )
        
        return {
            'id': TransactionDomain.generate_transaction_id(),
            'descricao': descricao.strip(),
            'valor': valor,
            'tipo': tipo,
            'data_transacao': data_transacao,
            'categoria': categoria,
            'conta_id': conta_id,
            'cartao_id': cartao_id,
            'parcelamento': parcelamento,
            'observacoes': observacoes,
            'status': StatusTransacao.PROCESSADA,  # Regra: inicia como processada
            'compartilhado_com_alzi': compartilhado_com_alzi,
            'created_at': now,
            'updated_at': now
        }

    @staticmethod
    def can_transaction_be_deleted(
        transaction: Transacao
    ) -> Dict[str, Any]:
        """
        Verifica se uma transação pode ser excluída
        
        Args:
            transaction: Transação a ser verificada
            
        Returns:
            Dict com 'can_delete': bool e 'reason': str
        """
        if transaction.status == StatusTransacao.CANCELADA:
            return {
                'can_delete': False,
                'reason': 'Transação já está cancelada'
            }
            
        # Verificar se é parte de um parcelamento pago
        if transaction.parcelamento:
            parcelas_pagas = [p for p in transaction.parcelamento if p.pago]
            if parcelas_pagas:
                return {
                    'can_delete': False,
                    'reason': 'Transação possui parcelas já pagas'
                }
        
        return {
            'can_delete': True,
            'reason': ''
        }

    @staticmethod
    def calculate_transaction_impact(
        transaction_value: float,
        transaction_type: TipoTransacao,
        account_balance: Optional[float] = None,
        card_available_limit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calcula impacto de uma transação em saldos e limites
        
        Args:
            transaction_value: Valor da transação
            transaction_type: Tipo da transação
            account_balance: Saldo atual da conta (se aplicável)
            card_available_limit: Limite disponível do cartão (se aplicável)
            
        Returns:
            Dict com impacts calculados
        """
        impact = {
            'account_balance_change': 0,
            'card_limit_change': 0,
            'new_account_balance': account_balance,
            'new_card_available_limit': card_available_limit
        }
        
        if account_balance is not None:
            if transaction_type == TipoTransacao.DEBITO:
                impact['account_balance_change'] = -transaction_value
                impact['new_account_balance'] = account_balance - transaction_value
            else:  # CREDITO
                impact['account_balance_change'] = transaction_value
                impact['new_account_balance'] = account_balance + transaction_value
                
        if card_available_limit is not None and transaction_type == TipoTransacao.DEBITO:
            impact['card_limit_change'] = -transaction_value
            impact['new_card_available_limit'] = card_available_limit - transaction_value
            
        return impact

    @staticmethod
    def group_transactions_by_invoice(
        transactions: List[Transacao],
        closing_day: int
    ) -> Dict[str, List[Transacao]]:
        """
        Agrupa transações por período de fatura
        
        Args:
            transactions: Lista de transações
            closing_day: Dia de fechamento do cartão
            
        Returns:
            Dict com chave 'YYYY-MM' e lista de transações da fatura
        """
        grouped = {}
        
        for transaction in transactions:
            transaction_date = datetime.fromisoformat(
                transaction.data_transacao.replace('Z', '+00:00')
            ).date()
            
            invoice_month, invoice_year = TransactionDomain.calculate_invoice_month_for_transaction(
                transaction_date, closing_day
            )
            
            key = f"{invoice_year}-{invoice_month:02d}"
            
            if key not in grouped:
                grouped[key] = []
                
            grouped[key].append(transaction)
            
        return grouped