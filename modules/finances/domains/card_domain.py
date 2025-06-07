"""
Domínio de Cartões de Crédito - Regras de Negócio

Esta classe contém todas as regras de negócio relacionadas a cartões de crédito,
incluindo limites, datas de vencimento, bandeiras e cálculos de fatura.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
import uuid
from calendar import monthrange

from utils.finance_models import CartaoCredito, BandeiraCartao


class CardDomain:
    """
    Domínio responsável pelas regras de negócio de cartões de crédito
    """

    @staticmethod
    def validate_card_data(
        nome: str,
        banco: str,
        bandeira: BandeiraCartao,
        limite: float,
        dia_vencimento: int,
        dia_fechamento: int
    ) -> Dict[str, Any]:
        """
        Valida dados de cartão de crédito
        
        Returns:
            Dict com 'valid': bool e 'errors': List[str]
        """
        errors = []
        
        # Validar nome
        if not nome or len(nome.strip()) < 2:
            errors.append("Nome do cartão deve ter pelo menos 2 caracteres")
        
        # Validar banco
        if not banco or len(banco.strip()) < 2:
            errors.append("Nome do banco deve ter pelo menos 2 caracteres")
            
        # Validar bandeira
        if not isinstance(bandeira, BandeiraCartao):
            errors.append("Bandeira do cartão inválida")
            
        # Validar limite
        if limite <= 0:
            errors.append("Limite do cartão deve ser maior que zero")
            
        # Validar dia de vencimento
        if not CardDomain.validate_due_date(dia_vencimento):
            errors.append("Dia de vencimento deve estar entre 1 e 31")
            
        # Validar dia de fechamento
        if not CardDomain.validate_closing_date(dia_fechamento):
            errors.append("Dia de fechamento deve estar entre 1 e 31")
            
        # Validar relacionamento entre datas
        if dia_vencimento == dia_fechamento:
            errors.append("Dia de vencimento deve ser diferente do dia de fechamento")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def validate_due_date(day: int) -> bool:
        """Valida dia de vencimento (1-31)"""
        return isinstance(day, int) and 1 <= day <= 31

    @staticmethod
    def validate_closing_date(day: int) -> bool:
        """Valida dia de fechamento (1-31)"""
        return isinstance(day, int) and 1 <= day <= 31

    @staticmethod
    def calculate_available_limit_after_purchase(
        current_available: float,
        transaction_value: float
    ) -> float:
        """
        Calcula limite disponível após compra
        
        Args:
            current_available: Limite disponível atual
            transaction_value: Valor da transação
            
        Returns:
            Novo limite disponível
        """
        # Usar Decimal para precisão monetária
        current = Decimal(str(current_available))
        value = Decimal(str(transaction_value))
        
        new_available = current - value
        
        # Limite disponível não pode ser negativo
        new_available = max(new_available, Decimal('0'))
        
        return float(new_available.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def restore_available_limit_after_cancellation(
        current_available: float,
        total_limit: float,
        transaction_value: float
    ) -> float:
        """
        Restaura limite disponível após cancelamento de transação
        
        Args:
            current_available: Limite disponível atual
            total_limit: Limite total do cartão
            transaction_value: Valor da transação cancelada
            
        Returns:
            Novo limite disponível restaurado
        """
        # Usar Decimal para precisão monetária
        current = Decimal(str(current_available))
        total = Decimal(str(total_limit))
        value = Decimal(str(transaction_value))
        
        new_available = current + value
        
        # Limite disponível não pode exceder o limite total
        new_available = min(new_available, total)
        
        return float(new_available.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def can_make_purchase(
        available_limit: float,
        purchase_value: float
    ) -> Dict[str, Any]:
        """
        Verifica se é possível fazer uma compra com o limite disponível
        
        Args:
            available_limit: Limite disponível
            purchase_value: Valor da compra
            
        Returns:
            Dict com 'can_purchase': bool e 'message': str
        """
        if purchase_value <= 0:
            return {
                'can_purchase': False,
                'message': 'Valor da compra deve ser maior que zero'
            }
            
        if purchase_value > available_limit:
            return {
                'can_purchase': False,
                'message': f'Limite insuficiente. Disponível: R$ {available_limit:.2f}'
            }
            
        return {
            'can_purchase': True,
            'message': ''
        }

    @staticmethod
    def calculate_invoice_period(
        closing_day: int,
        reference_month: int,
        reference_year: int
    ) -> Tuple[date, date]:
        """
        Calcula período de fatura baseado no dia de fechamento
        
        Args:
            closing_day: Dia de fechamento do cartão
            reference_month: Mês de referência da fatura
            reference_year: Ano de referência da fatura
            
        Returns:
            Tupla com (data_inicio, data_fim) do período da fatura
        """
        # Início do período: dia seguinte ao fechamento do mês anterior
        if reference_month == 1:
            prev_month = 12
            prev_year = reference_year - 1
        else:
            prev_month = reference_month - 1
            prev_year = reference_year
            
        # Ajustar dia de fechamento se não existir no mês anterior
        prev_month_days = monthrange(prev_year, prev_month)[1]
        adjusted_closing_day = min(closing_day, prev_month_days)
        
        start_date = date(prev_year, prev_month, adjusted_closing_day)
        
        # Fim do período: dia de fechamento do mês de referência
        current_month_days = monthrange(reference_year, reference_month)[1]
        adjusted_current_closing = min(closing_day, current_month_days)
        
        end_date = date(reference_year, reference_month, adjusted_current_closing)
        
        return start_date, end_date

    @staticmethod
    def determine_invoice_month_for_transaction(
        transaction_date: date,
        closing_day: int
    ) -> Tuple[int, int]:
        """
        Determina em qual mês/ano de fatura uma transação deve aparecer
        
        Args:
            transaction_date: Data da transação
            closing_day: Dia de fechamento do cartão
            
        Returns:
            Tupla com (mês, ano) da fatura
        """
        # Ajustar dia de fechamento para o mês da transação
        month_days = monthrange(transaction_date.year, transaction_date.month)[1]
        adjusted_closing_day = min(closing_day, month_days)
        
        closing_date_this_month = date(
            transaction_date.year,
            transaction_date.month,
            adjusted_closing_day
        )
        
        # Se a transação foi após o fechamento, vai para a próxima fatura
        if transaction_date > closing_date_this_month:
            if transaction_date.month == 12:
                return 1, transaction_date.year + 1
            else:
                return transaction_date.month + 1, transaction_date.year
        else:
            # Se foi antes/no fechamento, vai para a fatura atual
            return transaction_date.month, transaction_date.year

    @staticmethod
    def calculate_cards_summary(cards: List[CartaoCredito]) -> Dict[str, Any]:
        """
        Calcula resumo dos cartões de crédito
        
        Args:
            cards: Lista de cartões
            
        Returns:
            Dict com estatísticas dos cartões
        """
        active_cards = [card for card in cards if card.ativo]
        
        total_limit = sum(
            Decimal(str(card.limite)) for card in active_cards
        )
        
        total_available = sum(
            Decimal(str(card.limite_disponivel)) for card in active_cards
        )
        
        used_limit = total_limit - total_available
        
        shared_cards = [card for card in active_cards if card.compartilhado_com_alzi]
        
        # Estatísticas por bandeira
        brands_stats = {}
        for bandeira in BandeiraCartao:
            brand_cards = [card for card in active_cards if card.bandeira == bandeira]
            if brand_cards:
                brands_stats[bandeira.value] = {
                    'count': len(brand_cards),
                    'total_limit': float(
                        sum(Decimal(str(card.limite)) for card in brand_cards)
                        .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    ),
                    'available_limit': float(
                        sum(Decimal(str(card.limite_disponivel)) for card in brand_cards)
                        .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    )
                }
        
        return {
            'total_cards': len(active_cards),
            'total_limit': float(total_limit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_available': float(total_available.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'used_limit': float(used_limit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'usage_percentage': float(
                (used_limit / total_limit * 100) if total_limit > 0 else 0
            ),
            'shared_cards_count': len(shared_cards),
            'brands_stats': brands_stats,
            'inactive_cards': len(cards) - len(active_cards)
        }

    @staticmethod
    def generate_card_id() -> str:
        """Gera ID único para novo cartão"""
        return str(uuid.uuid4())

    @staticmethod
    def prepare_card_creation_data(
        nome: str,
        banco: str,
        bandeira: BandeiraCartao,
        limite: float,
        dia_vencimento: int,
        dia_fechamento: int,
        conta_vinculada_id: Optional[str] = None,
        compartilhado_com_alzi: bool = False
    ) -> Dict[str, Any]:
        """
        Prepara dados para criação de cartão com regras de negócio aplicadas
        
        Returns:
            Dict com dados preparados para criação
        """
        now = datetime.now().isoformat()
        
        return {
            'id': CardDomain.generate_card_id(),
            'nome': nome.strip(),
            'banco': banco.strip(),
            'bandeira': bandeira,
            'limite': limite,
            'limite_disponivel': limite,  # Regra: limite disponível = limite total na criação
            'conta_vinculada_id': conta_vinculada_id,
            'dia_vencimento': dia_vencimento,
            'dia_fechamento': dia_fechamento,
            'compartilhado_com_alzi': compartilhado_com_alzi,
            'ativo': True,  # Regra: cartão sempre inicia ativo
            'created_at': now,
            'updated_at': now
        }

    @staticmethod
    def can_card_be_deleted(
        card: CartaoCredito,
        has_transactions: bool
    ) -> Dict[str, Any]:
        """
        Verifica se um cartão pode ser excluído
        
        Args:
            card: Cartão a ser verificado
            has_transactions: Se o cartão possui transações
            
        Returns:
            Dict com 'can_delete': bool e 'reason': str
        """
        if has_transactions:
            return {
                'can_delete': False,
                'reason': 'Cartão possui transações. Use inativação ao invés de exclusão.'
            }
            
        if card.limite_disponivel != card.limite:
            return {
                'can_delete': False,
                'reason': 'Cartão possui limite utilizado. Quite as pendências primeiro.'
            }
            
        return {
            'can_delete': True,
            'reason': ''
        }

    @staticmethod
    def filter_cards_by_criteria(
        cards: List[CartaoCredito],
        ativos_apenas: bool = True,
        compartilhados_apenas: Optional[bool] = None,
        bandeira: Optional[BandeiraCartao] = None
    ) -> List[CartaoCredito]:
        """
        Filtra cartões por critérios específicos
        
        Args:
            cards: Lista de cartões
            ativos_apenas: Filtrar apenas cartões ativos
            compartilhados_apenas: Filtrar apenas compartilhados (None = todos)
            bandeira: Filtrar por bandeira específica (None = todas)
            
        Returns:
            Lista filtrada de cartões
        """
        filtered = cards
        
        if ativos_apenas:
            filtered = [card for card in filtered if card.ativo]
            
        if compartilhados_apenas is not None:
            filtered = [card for card in filtered 
                       if card.compartilhado_com_alzi == compartilhados_apenas]
            
        if bandeira is not None:
            filtered = [card for card in filtered if card.bandeira == bandeira]
            
        return filtered