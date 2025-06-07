"""
Domínio Alzi - Regras de Negócio para Gastos Compartilhados

Esta classe contém todas as regras de negócio relacionadas ao compartilhamento
de gastos com Alzi, incluindo cálculos de divisão e relatórios.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP

from utils.finance_models import (
    Transacao, ContaCorrente, CartaoCredito, TipoTransacao
)


class AlziDomain:
    """
    Domínio responsável pelas regras de negócio de gastos compartilhados com Alzi
    """

    # Constante: Percentual de divisão com Alzi
    ALZI_SHARE_PERCENTAGE = Decimal('0.5')  # 50%

    @staticmethod
    def calculate_shared_amount(valor_total: float) -> Dict[str, float]:
        """
        Calcula valores compartilhados com Alzi (divisão 50/50)
        
        Args:
            valor_total: Valor total da transação
            
        Returns:
            Dict com valores calculados
        """
        total = Decimal(str(valor_total))
        shared_amount = total * AlziDomain.ALZI_SHARE_PERCENTAGE
        my_amount = total - shared_amount
        
        return {
            'valor_total': float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'valor_alzi': float(shared_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'valor_meu': float(my_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }

    @staticmethod
    def calculate_monthly_shared_summary(
        shared_transactions: List[Transacao]
    ) -> Dict[str, Any]:
        """
        Calcula resumo mensal de gastos compartilhados
        
        Args:
            shared_transactions: Lista de transações compartilhadas
            
        Returns:
            Dict com resumo dos gastos compartilhados
        """
        if not shared_transactions:
            return {
                'total_transactions': 0,
                'valor_total_gastos': 0.0,
                'valor_alzi_deve': 0.0,
                'valor_meu': 0.0,
                'por_categoria': {},
                'por_fonte': {'conta': 0.0, 'cartao': 0.0},
                'maior_gasto': None,
                'menor_gasto': None
            }
        
        # Filtrar apenas débitos (gastos)
        gastos_compartilhados = [
            t for t in shared_transactions 
            if t.tipo == TipoTransacao.DEBITO
        ]
        
        if not gastos_compartilhados:
            return AlziDomain.calculate_monthly_shared_summary([])
        
        total_gastos = sum(Decimal(str(t.valor)) for t in gastos_compartilhados)
        valor_alzi = total_gastos * AlziDomain.ALZI_SHARE_PERCENTAGE
        valor_meu = total_gastos - valor_alzi
        
        # Agregar por categoria
        por_categoria = {}
        for transacao in gastos_compartilhados:
            categoria = transacao.categoria or 'Sem categoria'
            if categoria not in por_categoria:
                por_categoria[categoria] = {
                    'quantidade': 0,
                    'valor_total': Decimal('0'),
                    'valor_alzi': Decimal('0')
                }
            
            valor_transacao = Decimal(str(transacao.valor))
            por_categoria[categoria]['quantidade'] += 1
            por_categoria[categoria]['valor_total'] += valor_transacao
            por_categoria[categoria]['valor_alzi'] += valor_transacao * AlziDomain.ALZI_SHARE_PERCENTAGE
        
        # Converter para float
        for categoria in por_categoria:
            por_categoria[categoria]['valor_total'] = float(
                por_categoria[categoria]['valor_total'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            por_categoria[categoria]['valor_alzi'] = float(
                por_categoria[categoria]['valor_alzi'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
        
        # Agregar por fonte (conta vs cartão)
        por_fonte = {'conta': Decimal('0'), 'cartao': Decimal('0')}
        for transacao in gastos_compartilhados:
            if transacao.conta_id:
                por_fonte['conta'] += Decimal(str(transacao.valor))
            elif transacao.cartao_id:
                por_fonte['cartao'] += Decimal(str(transacao.valor))
        
        # Encontrar maior e menor gasto
        valores = [t.valor for t in gastos_compartilhados]
        maior_valor = max(valores)
        menor_valor = min(valores)
        
        maior_gasto = next(t for t in gastos_compartilhados if t.valor == maior_valor)
        menor_gasto = next(t for t in gastos_compartilhados if t.valor == menor_valor)
        
        return {
            'total_transactions': len(gastos_compartilhados),
            'valor_total_gastos': float(total_gastos.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'valor_alzi_deve': float(valor_alzi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'valor_meu': float(valor_meu.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'por_categoria': por_categoria,
            'por_fonte': {
                'conta': float(por_fonte['conta'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'cartao': float(por_fonte['cartao'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            },
            'maior_gasto': {
                'descricao': maior_gasto.descricao,
                'valor': maior_gasto.valor,
                'valor_alzi': float((Decimal(str(maior_gasto.valor)) * AlziDomain.ALZI_SHARE_PERCENTAGE)
                                  .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'data': maior_gasto.data_transacao,
                'categoria': maior_gasto.categoria
            },
            'menor_gasto': {
                'descricao': menor_gasto.descricao,
                'valor': menor_gasto.valor,
                'valor_alzi': float((Decimal(str(menor_gasto.valor)) * AlziDomain.ALZI_SHARE_PERCENTAGE)
                                  .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'data': menor_gasto.data_transacao,
                'categoria': menor_gasto.categoria
            }
        }

    @staticmethod
    def group_shared_transactions_by_invoice(
        shared_transactions: List[Transacao],
        closing_day: int
    ) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa transações compartilhadas por fatura de cartão
        
        Args:
            shared_transactions: Lista de transações compartilhadas
            closing_day: Dia de fechamento do cartão
            
        Returns:
            Dict com faturas e seus respectivos gastos compartilhados
        """
        # Importação local para evitar dependência circular
        from .transaction_domain import TransactionDomain
        
        # Filtrar apenas transações de cartão
        card_transactions = [
            t for t in shared_transactions 
            if t.cartao_id and t.tipo == TipoTransacao.DEBITO
        ]
        
        if not card_transactions:
            return {}
        
        # Agrupar por fatura
        grouped = {}
        
        for transaction in card_transactions:
            transaction_date = datetime.fromisoformat(
                transaction.data_transacao.replace('Z', '+00:00')
            ).date()
            
            invoice_month, invoice_year = TransactionDomain.calculate_invoice_month_for_transaction(
                transaction_date, closing_day
            )
            
            key = f"{invoice_year}-{invoice_month:02d}"
            
            if key not in grouped:
                grouped[key] = {
                    'ano': invoice_year,
                    'mes': invoice_month,
                    'transacoes': [],
                    'valor_total': Decimal('0'),
                    'valor_alzi': Decimal('0')
                }
            
            grouped[key]['transacoes'].append(transaction)
            valor_transacao = Decimal(str(transaction.valor))
            grouped[key]['valor_total'] += valor_transacao
            grouped[key]['valor_alzi'] += valor_transacao * AlziDomain.ALZI_SHARE_PERCENTAGE
        
        # Converter valores para float
        for key in grouped:
            grouped[key]['valor_total'] = float(
                grouped[key]['valor_total'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            grouped[key]['valor_alzi'] = float(
                grouped[key]['valor_alzi'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            grouped[key]['quantidade'] = len(grouped[key]['transacoes'])
        
        return grouped

    @staticmethod
    def calculate_shared_accounts_summary(
        accounts: List[ContaCorrente]
    ) -> Dict[str, Any]:
        """
        Calcula resumo de contas compartilhadas com Alzi
        
        Args:
            accounts: Lista de todas as contas
            
        Returns:
            Dict com resumo das contas compartilhadas
        """
        shared_accounts = [acc for acc in accounts if acc.compartilhado_com_alzi and acc.ativa]
        
        if not shared_accounts:
            return {
                'total_contas': 0,
                'saldo_total': 0.0,
                'saldo_alzi_parte': 0.0,
                'por_tipo': {},
                'contas': []
            }
        
        saldo_total = sum(Decimal(str(acc.saldo_atual)) for acc in shared_accounts)
        saldo_alzi_parte = saldo_total * AlziDomain.ALZI_SHARE_PERCENTAGE
        
        # Agregar por tipo
        por_tipo = {}
        for conta in shared_accounts:
            tipo = conta.tipo.value
            if tipo not in por_tipo:
                por_tipo[tipo] = {
                    'quantidade': 0,
                    'saldo_total': Decimal('0')
                }
            
            por_tipo[tipo]['quantidade'] += 1
            por_tipo[tipo]['saldo_total'] += Decimal(str(conta.saldo_atual))
        
        # Converter para float
        for tipo in por_tipo:
            por_tipo[tipo]['saldo_total'] = float(
                por_tipo[tipo]['saldo_total'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
        
        # Preparar lista de contas com valores de Alzi
        contas_info = []
        for conta in shared_accounts:
            saldo_conta = Decimal(str(conta.saldo_atual))
            saldo_alzi = saldo_conta * AlziDomain.ALZI_SHARE_PERCENTAGE
            
            contas_info.append({
                'id': conta.id,
                'nome': conta.nome,
                'banco': conta.banco,
                'tipo': conta.tipo.value,
                'saldo_total': float(saldo_conta.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'saldo_alzi_parte': float(saldo_alzi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return {
            'total_contas': len(shared_accounts),
            'saldo_total': float(saldo_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'saldo_alzi_parte': float(saldo_alzi_parte.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'por_tipo': por_tipo,
            'contas': contas_info
        }

    @staticmethod
    def calculate_shared_cards_summary(
        cards: List[CartaoCredito]
    ) -> Dict[str, Any]:
        """
        Calcula resumo de cartões compartilhados com Alzi
        
        Args:
            cards: Lista de todos os cartões
            
        Returns:
            Dict com resumo dos cartões compartilhados
        """
        shared_cards = [card for card in cards if card.compartilhado_com_alzi and card.ativo]
        
        if not shared_cards:
            return {
                'total_cartoes': 0,
                'limite_total': 0.0,
                'limite_usado': 0.0,
                'limite_alzi_parte': 0.0,
                'por_bandeira': {},
                'cartoes': []
            }
        
        limite_total = sum(Decimal(str(card.limite)) for card in shared_cards)
        limite_disponivel = sum(Decimal(str(card.limite_disponivel)) for card in shared_cards)
        limite_usado = limite_total - limite_disponivel
        limite_alzi_parte = limite_usado * AlziDomain.ALZI_SHARE_PERCENTAGE
        
        # Agregar por bandeira
        por_bandeira = {}
        for card in shared_cards:
            bandeira = card.bandeira.value
            if bandeira not in por_bandeira:
                por_bandeira[bandeira] = {
                    'quantidade': 0,
                    'limite_total': Decimal('0'),
                    'limite_usado': Decimal('0')
                }
            
            por_bandeira[bandeira]['quantidade'] += 1
            por_bandeira[bandeira]['limite_total'] += Decimal(str(card.limite))
            por_bandeira[bandeira]['limite_usado'] += Decimal(str(card.limite)) - Decimal(str(card.limite_disponivel))
        
        # Converter para float
        for bandeira in por_bandeira:
            por_bandeira[bandeira]['limite_total'] = float(
                por_bandeira[bandeira]['limite_total'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            por_bandeira[bandeira]['limite_usado'] = float(
                por_bandeira[bandeira]['limite_usado'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
        
        # Preparar lista de cartões com valores de Alzi
        cartoes_info = []
        for card in shared_cards:
            limite_card = Decimal(str(card.limite))
            usado_card = limite_card - Decimal(str(card.limite_disponivel))
            alzi_parte = usado_card * AlziDomain.ALZI_SHARE_PERCENTAGE
            
            cartoes_info.append({
                'id': card.id,
                'nome': card.nome,
                'bandeira': card.bandeira.value,
                'limite_total': float(limite_card.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'limite_usado': float(usado_card.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'limite_alzi_parte': float(alzi_parte.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return {
            'total_cartoes': len(shared_cards),
            'limite_total': float(limite_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'limite_usado': float(limite_usado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'limite_alzi_parte': float(limite_alzi_parte.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'por_bandeira': por_bandeira,
            'cartoes': cartoes_info
        }

    @staticmethod
    def should_transaction_be_shared(
        descricao: str,
        categoria: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sugere se uma transação deveria ser compartilhada baseada na descrição/categoria
        
        Args:
            descricao: Descrição da transação
            categoria: Categoria da transação
            
        Returns:
            Dict com sugestão e motivo
        """
        # Palavras-chave que indicam gastos compartilhados
        shared_keywords = [
            'mercado', 'supermercado', 'ifood', 'uber eats', 'delivery',
            'restaurante', 'combustivel', 'posto', 'gasolina',
            'farmacia', 'medicamento', 'casa', 'lar', 'limpeza',
            'internet', 'energia', 'agua', 'gas', 'condominio',
            'streaming', 'netflix', 'spotify', 'amazon', 'prime'
        ]
        
        # Palavras-chave que indicam gastos pessoais  
        personal_keywords = [
            'roupa', 'vestuario', 'beleza', 'cabelo', 'academia',
            'curso', 'livro', 'presente', 'game', 'jogo',
            'trabalho', 'transporte individual', 'uber pessoal'
        ]
        
        desc_lower = descricao.lower()
        cat_lower = categoria.lower() if categoria else ''
        
        # Verificar palavras-chave compartilhadas
        shared_matches = [kw for kw in shared_keywords if kw in desc_lower or kw in cat_lower]
        
        # Verificar palavras-chave pessoais
        personal_matches = [kw for kw in personal_keywords if kw in desc_lower or kw in cat_lower]
        
        if shared_matches:
            return {
                'should_share': True,
                'confidence': 'alta',
                'reason': f"Palavras-chave compartilhadas encontradas: {', '.join(shared_matches)}"
            }
        
        if personal_matches:
            return {
                'should_share': False,
                'confidence': 'alta', 
                'reason': f"Palavras-chave pessoais encontradas: {', '.join(personal_matches)}"
            }
        
        return {
            'should_share': None,
            'confidence': 'baixa',
            'reason': 'Não foi possível determinar automaticamente'
        }

    @staticmethod
    def format_shared_value_display(
        valor_total: float
    ) -> Dict[str, str]:
        """
        Formata valores compartilhados para exibição
        
        Args:
            valor_total: Valor total da transação
            
        Returns:
            Dict com valores formatados
        """
        values = AlziDomain.calculate_shared_amount(valor_total)
        
        return {
            'total': f"R$ {values['valor_total']:.2f}",
            'alzi': f"R$ {values['valor_alzi']:.2f}",
            'meu': f"R$ {values['valor_meu']:.2f}",
            'percentual': "50%"
        }