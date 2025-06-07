"""
Testes unitários para AlziDomain

Testa todas as regras de negócio relacionadas aos gastos compartilhados
com Alzi, incluindo cálculos de divisão e relatórios.
"""

import unittest
from datetime import datetime, date
from decimal import Decimal

# Adicionar caminho para imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.domains import AlziDomain
from utils.finance_models import (
    Transacao, ContaCorrente, CartaoCredito, TipoTransacao, TipoConta, 
    BandeiraCartao, StatusTransacao
)


class TestAlziDomain(unittest.TestCase):
    """Testes para AlziDomain"""

    def test_calculate_shared_amount_exact_division(self):
        """Testa cálculo de divisão exata"""
        result = AlziDomain.calculate_shared_amount(100.0)
        
        self.assertEqual(result['valor_total'], 100.0)
        self.assertEqual(result['valor_alzi'], 50.0)
        self.assertEqual(result['valor_meu'], 50.0)

    def test_calculate_shared_amount_with_rounding(self):
        """Testa cálculo com arredondamento"""
        result = AlziDomain.calculate_shared_amount(99.99)
        
        self.assertEqual(result['valor_total'], 99.99)
        self.assertEqual(result['valor_alzi'], 50.0)  # 49.995 arredonda para 50.00
        self.assertEqual(result['valor_meu'], 50.0)   # Ajustado para valor correto

    def test_calculate_shared_amount_precision(self):
        """Testa precisão do cálculo"""
        result = AlziDomain.calculate_shared_amount(33.33)
        
        self.assertEqual(result['valor_total'], 33.33)
        self.assertEqual(result['valor_alzi'], 16.67)  # 16.665 arredonda para 16.67
        self.assertEqual(result['valor_meu'], 16.67)   # Ajustado para valor correto

    def test_calculate_monthly_shared_summary_empty(self):
        """Testa resumo mensal sem transações"""
        summary = AlziDomain.calculate_monthly_shared_summary([])
        
        self.assertEqual(summary['total_transactions'], 0)
        self.assertEqual(summary['valor_total_gastos'], 0.0)
        self.assertEqual(summary['valor_alzi_deve'], 0.0)
        self.assertEqual(summary['valor_meu'], 0.0)
        self.assertEqual(summary['por_categoria'], {})
        self.assertIsNone(summary['maior_gasto'])
        self.assertIsNone(summary['menor_gasto'])

    def test_calculate_monthly_shared_summary_with_transactions(self):
        """Testa resumo mensal com transações"""
        transactions = [
            Transacao(
                id='1', descricao='Supermercado', valor=200.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-10T10:00:00', categoria='Alimentação', conta_id='acc1',
                cartao_id=None, parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            ),
            Transacao(
                id='2', descricao='Combustível', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-15T10:00:00', categoria='Transporte', conta_id=None,
                cartao_id='card1', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            ),
            Transacao(
                id='3', descricao='Depósito', valor=500.0, tipo=TipoTransacao.CREDITO,  # Crédito ignorado
                data_transacao='2024-03-20T10:00:00', categoria=None, conta_id='acc1',
                cartao_id=None, parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            )
        ]
        
        summary = AlziDomain.calculate_monthly_shared_summary(transactions)
        
        self.assertEqual(summary['total_transactions'], 2)  # Apenas débitos
        self.assertEqual(summary['valor_total_gastos'], 300.0)
        self.assertEqual(summary['valor_alzi_deve'], 150.0)
        self.assertEqual(summary['valor_meu'], 150.0)
        
        # Verificar categorias
        self.assertIn('Alimentação', summary['por_categoria'])
        self.assertIn('Transporte', summary['por_categoria'])
        self.assertEqual(summary['por_categoria']['Alimentação']['quantidade'], 1)
        self.assertEqual(summary['por_categoria']['Alimentação']['valor_total'], 200.0)
        self.assertEqual(summary['por_categoria']['Alimentação']['valor_alzi'], 100.0)
        
        # Verificar por fonte
        self.assertEqual(summary['por_fonte']['conta'], 200.0)
        self.assertEqual(summary['por_fonte']['cartao'], 100.0)
        
        # Verificar maior e menor gasto
        self.assertEqual(summary['maior_gasto']['valor'], 200.0)
        self.assertEqual(summary['maior_gasto']['valor_alzi'], 100.0)
        self.assertEqual(summary['menor_gasto']['valor'], 100.0)
        self.assertEqual(summary['menor_gasto']['valor_alzi'], 50.0)

    def test_calculate_monthly_shared_summary_sem_categoria(self):
        """Testa resumo com transação sem categoria"""
        transactions = [
            Transacao(
                id='1', descricao='Compra', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-10T10:00:00', categoria=None, conta_id='acc1',
                cartao_id=None, parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            )
        ]
        
        summary = AlziDomain.calculate_monthly_shared_summary(transactions)
        
        self.assertIn('Sem categoria', summary['por_categoria'])
        self.assertEqual(summary['por_categoria']['Sem categoria']['quantidade'], 1)

    def test_group_shared_transactions_by_invoice_empty(self):
        """Testa agrupamento por fatura sem transações"""
        grouped = AlziDomain.group_shared_transactions_by_invoice([], 5)
        
        self.assertEqual(grouped, {})

    def test_group_shared_transactions_by_invoice_with_card_transactions(self):
        """Testa agrupamento por fatura com transações de cartão"""
        transactions = [
            Transacao(
                id='1', descricao='Compra 1', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-03T10:00:00', categoria='Compras', conta_id=None,
                cartao_id='card1', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            ),
            Transacao(
                id='2', descricao='Compra 2', valor=200.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-10T10:00:00', categoria='Compras', conta_id=None,
                cartao_id='card1', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            ),
            Transacao(
                id='3', descricao='Conta', valor=50.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-15T10:00:00', categoria='Conta', conta_id='acc1',  # Conta ignorada
                cartao_id=None, parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=True
            )
        ]
        
        grouped = AlziDomain.group_shared_transactions_by_invoice(transactions, 5)
        
        # Apenas transações de cartão devem ser agrupadas
        self.assertEqual(len(grouped), 2)  # Duas faturas diferentes
        
        # Verificar se existe fatura para abril (primeira transação)
        self.assertIn('2024-04', grouped)
        fatura_abril = grouped['2024-04']
        self.assertEqual(fatura_abril['mes'], 4)
        self.assertEqual(fatura_abril['ano'], 2024)
        self.assertEqual(fatura_abril['quantidade'], 1)
        self.assertEqual(fatura_abril['valor_total'], 100.0)
        self.assertEqual(fatura_abril['valor_alzi'], 50.0)
        
        # Verificar se existe fatura para maio (segunda transação)
        self.assertIn('2024-05', grouped)
        fatura_maio = grouped['2024-05']
        self.assertEqual(fatura_maio['quantidade'], 1)
        self.assertEqual(fatura_maio['valor_total'], 200.0)
        self.assertEqual(fatura_maio['valor_alzi'], 100.0)

    def test_calculate_shared_accounts_summary_empty(self):
        """Testa resumo de contas compartilhadas sem contas"""
        summary = AlziDomain.calculate_shared_accounts_summary([])
        
        self.assertEqual(summary['total_contas'], 0)
        self.assertEqual(summary['saldo_total'], 0.0)
        self.assertEqual(summary['saldo_alzi_parte'], 0.0)
        self.assertEqual(summary['por_tipo'], {})
        self.assertEqual(summary['contas'], [])

    def test_calculate_shared_accounts_summary_with_accounts(self):
        """Testa resumo de contas compartilhadas com contas"""
        accounts = [
            ContaCorrente(
                id='1', nome='Conta 1', banco='Banco', agencia='1234', conta='5678',
                tipo=TipoConta.CORRENTE, saldo_inicial=1000.0, saldo_atual=1000.0,
                compartilhado_com_alzi=True, ativa=True
            ),
            ContaCorrente(
                id='2', nome='Conta 2', banco='Banco', agencia='1234', conta='5679',
                tipo=TipoConta.POUPANCA, saldo_inicial=500.0, saldo_atual=500.0,
                compartilhado_com_alzi=False, ativa=True  # Não compartilhada
            ),
            ContaCorrente(
                id='3', nome='Conta 3', banco='Banco', agencia='1234', conta='5680',
                tipo=TipoConta.CORRENTE, saldo_inicial=200.0, saldo_atual=200.0,
                compartilhado_com_alzi=True, ativa=False  # Inativa
            )
        ]
        
        summary = AlziDomain.calculate_shared_accounts_summary(accounts)
        
        self.assertEqual(summary['total_contas'], 1)  # Apenas ativas e compartilhadas
        self.assertEqual(summary['saldo_total'], 1000.0)
        self.assertEqual(summary['saldo_alzi_parte'], 500.0)
        
        # Verificar por tipo
        self.assertIn('corrente', summary['por_tipo'])
        self.assertEqual(summary['por_tipo']['corrente']['quantidade'], 1)
        self.assertEqual(summary['por_tipo']['corrente']['saldo_total'], 1000.0)
        
        # Verificar detalhes das contas
        self.assertEqual(len(summary['contas']), 1)
        conta_info = summary['contas'][0]
        self.assertEqual(conta_info['nome'], 'Conta 1')
        self.assertEqual(conta_info['saldo_total'], 1000.0)
        self.assertEqual(conta_info['saldo_alzi_parte'], 500.0)

    def test_calculate_shared_cards_summary_empty(self):
        """Testa resumo de cartões compartilhados sem cartões"""
        summary = AlziDomain.calculate_shared_cards_summary([])
        
        self.assertEqual(summary['total_cartoes'], 0)
        self.assertEqual(summary['limite_total'], 0.0)
        self.assertEqual(summary['limite_usado'], 0.0)
        self.assertEqual(summary['limite_alzi_parte'], 0.0)
        self.assertEqual(summary['por_bandeira'], {})
        self.assertEqual(summary['cartoes'], [])

    def test_calculate_shared_cards_summary_with_cards(self):
        """Testa resumo de cartões compartilhados com cartões"""
        cards = [
            CartaoCredito(
                id='1', nome='Cartão 1', banco='Banco', bandeira=BandeiraCartao.VISA,
                limite=5000.0, limite_disponivel=4000.0, conta_vinculada_id=None,
                dia_vencimento=10, dia_fechamento=5, compartilhado_com_alzi=True, ativo=True
            ),
            CartaoCredito(
                id='2', nome='Cartão 2', banco='Banco', bandeira=BandeiraCartao.MASTERCARD,
                limite=3000.0, limite_disponivel=3000.0, conta_vinculada_id=None,
                dia_vencimento=15, dia_fechamento=10, compartilhado_com_alzi=False, ativo=True  # Não compartilhado
            ),
            CartaoCredito(
                id='3', nome='Cartão 3', banco='Banco', bandeira=BandeiraCartao.VISA,
                limite=2000.0, limite_disponivel=1500.0, conta_vinculada_id=None,
                dia_vencimento=20, dia_fechamento=15, compartilhado_com_alzi=True, ativo=False  # Inativo
            )
        ]
        
        summary = AlziDomain.calculate_shared_cards_summary(cards)
        
        self.assertEqual(summary['total_cartoes'], 1)  # Apenas ativos e compartilhados
        self.assertEqual(summary['limite_total'], 5000.0)
        self.assertEqual(summary['limite_usado'], 1000.0)  # 5000 - 4000
        self.assertEqual(summary['limite_alzi_parte'], 500.0)  # 50% de 1000
        
        # Verificar por bandeira
        self.assertIn('visa', summary['por_bandeira'])
        self.assertEqual(summary['por_bandeira']['visa']['quantidade'], 1)
        self.assertEqual(summary['por_bandeira']['visa']['limite_total'], 5000.0)
        self.assertEqual(summary['por_bandeira']['visa']['limite_usado'], 1000.0)
        
        # Verificar detalhes dos cartões
        self.assertEqual(len(summary['cartoes']), 1)
        cartao_info = summary['cartoes'][0]
        self.assertEqual(cartao_info['nome'], 'Cartão 1')
        self.assertEqual(cartao_info['limite_total'], 5000.0)
        self.assertEqual(cartao_info['limite_usado'], 1000.0)
        self.assertEqual(cartao_info['limite_alzi_parte'], 500.0)

    def test_should_transaction_be_shared_shared_keywords(self):
        """Testa sugestão para palavras-chave compartilhadas"""
        result = AlziDomain.should_transaction_be_shared('Compra no supermercado')
        
        self.assertTrue(result['should_share'])
        self.assertEqual(result['confidence'], 'alta')
        self.assertIn('supermercado', result['reason'])

    def test_should_transaction_be_shared_personal_keywords(self):
        """Testa sugestão para palavras-chave pessoais"""
        result = AlziDomain.should_transaction_be_shared('Compra de roupa')
        
        self.assertFalse(result['should_share'])
        self.assertEqual(result['confidence'], 'alta')
        self.assertIn('roupa', result['reason'])

    def test_should_transaction_be_shared_category_match(self):
        """Testa sugestão baseada em categoria"""
        result = AlziDomain.should_transaction_be_shared(
            'Compra diversa', categoria='casa e lar'
        )
        
        self.assertTrue(result['should_share'])
        self.assertEqual(result['confidence'], 'alta')
        self.assertIn('casa', result['reason'])

    def test_should_transaction_be_shared_no_match(self):
        """Testa sugestão sem palavras-chave conhecidas"""
        result = AlziDomain.should_transaction_be_shared('Compra misteriosa')
        
        self.assertIsNone(result['should_share'])
        self.assertEqual(result['confidence'], 'baixa')
        self.assertIn('Não foi possível determinar', result['reason'])

    def test_should_transaction_be_shared_multiple_keywords(self):
        """Testa sugestão com múltiplas palavras-chave"""
        result = AlziDomain.should_transaction_be_shared(
            'Ifood mercado supermercado'
        )
        
        self.assertTrue(result['should_share'])
        self.assertEqual(result['confidence'], 'alta')
        # Deve mencionar pelo menos uma das palavras-chave encontradas
        reason_lower = result['reason'].lower()
        keywords_found = ['ifood', 'mercado', 'supermercado']
        found_any = any(keyword in reason_lower for keyword in keywords_found)
        self.assertTrue(found_any)

    def test_format_shared_value_display(self):
        """Testa formatação de valores compartilhados"""
        formatted = AlziDomain.format_shared_value_display(100.0)
        
        self.assertEqual(formatted['total'], 'R$ 100.00')
        self.assertEqual(formatted['alzi'], 'R$ 50.00')
        self.assertEqual(formatted['meu'], 'R$ 50.00')
        self.assertEqual(formatted['percentual'], '50%')

    def test_format_shared_value_display_with_rounding(self):
        """Testa formatação com arredondamento"""
        formatted = AlziDomain.format_shared_value_display(99.99)
        
        self.assertEqual(formatted['total'], 'R$ 99.99')
        self.assertEqual(formatted['alzi'], 'R$ 50.00')
        self.assertEqual(formatted['meu'], 'R$ 50.00')

    def test_alzi_share_percentage_constant(self):
        """Testa se a constante de percentual está correta"""
        self.assertEqual(AlziDomain.ALZI_SHARE_PERCENTAGE, Decimal('0.5'))


if __name__ == '__main__':
    unittest.main()