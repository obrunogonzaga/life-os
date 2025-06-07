"""
Testes unitários para TransactionDomain

Testa todas as regras de negócio relacionadas a transações,
incluindo parcelamento, validações e cálculos de fatura.
"""

import unittest
from datetime import datetime, date
from decimal import Decimal

# Adicionar caminho para imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.domains import TransactionDomain
from utils.finance_models import Transacao, TipoTransacao, StatusTransacao, Parcelamento


class TestTransactionDomain(unittest.TestCase):
    """Testes para TransactionDomain"""

    def setUp(self):
        """Setup para cada teste"""
        self.valid_transaction_data = {
            'descricao': 'Compra Teste',
            'valor': 100.0,
            'tipo': TipoTransacao.DEBITO,
            'data_transacao': '2024-03-10T10:00:00',
            'cartao_id': 'card123',
            'parcelas': 1
        }

    def test_validate_transaction_data_valid(self):
        """Testa validação com dados válidos"""
        result = TransactionDomain.validate_transaction_data(**self.valid_transaction_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_validate_transaction_data_invalid_descricao(self):
        """Testa validação com descrição inválida"""
        data = self.valid_transaction_data.copy()
        data['descricao'] = 'A'  # Muito curto
        
        result = TransactionDomain.validate_transaction_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Descrição deve ter pelo menos 2 caracteres', result['errors'])

    def test_validate_transaction_data_invalid_valor(self):
        """Testa validação com valor inválido"""
        data = self.valid_transaction_data.copy()
        data['valor'] = 0.0  # Zero
        
        result = TransactionDomain.validate_transaction_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Valor deve ser maior que zero', result['errors'])

    def test_validate_transaction_data_no_account_or_card(self):
        """Testa validação sem conta nem cartão"""
        data = self.valid_transaction_data.copy()
        del data['cartao_id']  # Remove cartão, sem conta
        
        result = TransactionDomain.validate_transaction_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Transação deve ter uma conta ou cartão vinculado', result['errors'])

    def test_validate_transaction_data_both_account_and_card(self):
        """Testa validação com conta E cartão"""
        data = self.valid_transaction_data.copy()
        data['conta_id'] = 'account123'  # Adiciona conta mantendo cartão
        
        result = TransactionDomain.validate_transaction_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Transação não pode ter conta e cartão vinculados simultaneamente', result['errors'])

    def test_validate_transaction_data_invalid_parcelas_credito(self):
        """Testa validação de parcelamento para crédito"""
        data = self.valid_transaction_data.copy()
        data['tipo'] = TipoTransacao.CREDITO
        data['parcelas'] = 3  # Parcelamento só para débito
        
        result = TransactionDomain.validate_transaction_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Parcelamento só é permitido para débitos (compras) em cartão', result['errors'])

    def test_validate_transaction_data_invalid_parcelas_count(self):
        """Testa validação de número de parcelas inválido"""
        data = self.valid_transaction_data.copy()
        data['parcelas'] = 70  # Muito alto
        
        result = TransactionDomain.validate_transaction_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Número de parcelas deve estar entre 1 e 60', result['errors'])

    def test_calculate_installments_single(self):
        """Testa cálculo de parcelamento para 1 parcela"""
        installments = TransactionDomain.calculate_installments(100.0, 1, '2024-03-10T10:00:00')
        
        self.assertEqual(len(installments), 0)  # Não gera parcelamento para 1x

    def test_calculate_installments_multiple(self):
        """Testa cálculo de parcelamento para múltiplas parcelas"""
        installments = TransactionDomain.calculate_installments(300.0, 3, '2024-03-10T10:00:00')
        
        self.assertEqual(len(installments), 3)
        
        # Verificar primeira parcela
        self.assertEqual(installments[0].numero_parcela, 1)
        self.assertEqual(installments[0].total_parcelas, 3)
        self.assertEqual(installments[0].valor_parcela, 100.0)
        self.assertEqual(installments[0].data_vencimento[:10], '2024-03-10')
        self.assertFalse(installments[0].pago)
        
        # Verificar segunda parcela (mês seguinte)
        self.assertEqual(installments[1].numero_parcela, 2)
        self.assertEqual(installments[1].data_vencimento[:10], '2024-04-10')
        
        # Verificar terceira parcela
        self.assertEqual(installments[2].numero_parcela, 3)
        self.assertEqual(installments[2].data_vencimento[:10], '2024-05-10')

    def test_calculate_installments_february_adjustment(self):
        """Testa ajuste de data para fevereiro"""
        # Transação em 31/01, parcelada em 2x
        installments = TransactionDomain.calculate_installments(200.0, 2, '2024-01-31T10:00:00')
        
        self.assertEqual(len(installments), 2)
        
        # Segunda parcela deve ser 29/02 (2024 é bissexto)
        self.assertEqual(installments[1].data_vencimento[:10], '2024-02-29')

    def test_calculate_installments_rounding(self):
        """Testa arredondamento em parcelamento"""
        # R$ 100,00 em 3x = R$ 33,33 + R$ 33,33 + R$ 33,34
        installments = TransactionDomain.calculate_installments(100.0, 3, '2024-03-10T10:00:00')
        
        # Primeiras duas parcelas
        self.assertEqual(installments[0].valor_parcela, 33.33)
        self.assertEqual(installments[1].valor_parcela, 33.33)
        # Última parcela compensa o arredondamento
        self.assertEqual(installments[2].valor_parcela, 33.34)

    def test_calculate_invoice_month_for_transaction_before_closing(self):
        """Testa determinação de fatura para transação antes do fechamento"""
        invoice_month, invoice_year = TransactionDomain.calculate_invoice_month_for_transaction(
            date(2024, 3, 3), 5  # Transação dia 3, fechamento dia 5
        )
        
        # Deve ir para fatura de abril (próximo mês)
        self.assertEqual(invoice_month, 4)
        self.assertEqual(invoice_year, 2024)

    def test_calculate_invoice_month_for_transaction_after_closing(self):
        """Testa determinação de fatura para transação após fechamento"""
        invoice_month, invoice_year = TransactionDomain.calculate_invoice_month_for_transaction(
            date(2024, 3, 10), 5  # Transação dia 10, fechamento dia 5
        )
        
        # Deve ir para fatura de maio (2 meses à frente)
        self.assertEqual(invoice_month, 5)
        self.assertEqual(invoice_year, 2024)

    def test_calculate_invoice_period_for_card(self):
        """Testa cálculo de período de fatura"""
        start_date, end_date = TransactionDomain.calculate_invoice_period_for_card(5, 4, 2024)
        
        # Fatura de abril contém transações de 06/02 a 05/03
        self.assertEqual(start_date, date(2024, 2, 5))
        self.assertEqual(end_date, date(2024, 3, 5))

    def test_is_duplicate_transaction_true(self):
        """Testa detecção de transação duplicada"""
        existing_transactions = [
            Transacao(
                id='1', descricao='Compra', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-10T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            )
        ]
        
        new_transaction = {
            'data_transacao': '2024-03-10T15:00:00',  # Mesma data
            'valor': 100.0,  # Mesmo valor
            'cartao_id': 'card123'  # Mesmo cartão
        }
        
        is_duplicate = TransactionDomain.is_duplicate_transaction(
            existing_transactions, new_transaction
        )
        
        self.assertTrue(is_duplicate)

    def test_is_duplicate_transaction_false(self):
        """Testa não detecção de duplicata para transação diferente"""
        existing_transactions = [
            Transacao(
                id='1', descricao='Compra', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-10T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            )
        ]
        
        new_transaction = {
            'data_transacao': '2024-03-11T15:00:00',  # Data diferente
            'valor': 100.0,
            'cartao_id': 'card123'
        }
        
        is_duplicate = TransactionDomain.is_duplicate_transaction(
            existing_transactions, new_transaction
        )
        
        self.assertFalse(is_duplicate)

    def test_should_ignore_transaction_description_true(self):
        """Testa se deve ignorar descrição específica"""
        should_ignore = TransactionDomain.should_ignore_transaction_description('PAGAMENTO FATURA')
        self.assertTrue(should_ignore)
        
        should_ignore = TransactionDomain.should_ignore_transaction_description('SALDO ANTERIOR')
        self.assertTrue(should_ignore)
        
        should_ignore = TransactionDomain.should_ignore_transaction_description('ANUIDADE CARTAO')
        self.assertTrue(should_ignore)

    def test_should_ignore_transaction_description_false(self):
        """Testa se não deve ignorar descrição normal"""
        should_ignore = TransactionDomain.should_ignore_transaction_description('COMPRA SUPERMERCADO')
        self.assertFalse(should_ignore)
        
        should_ignore = TransactionDomain.should_ignore_transaction_description('RESTAURANTE TESTE')
        self.assertFalse(should_ignore)

    def test_calculate_reversal_transaction_type(self):
        """Testa cálculo de tipo reverso"""
        reversal = TransactionDomain.calculate_reversal_transaction_type(TipoTransacao.DEBITO)
        self.assertEqual(reversal, TipoTransacao.CREDITO)
        
        reversal = TransactionDomain.calculate_reversal_transaction_type(TipoTransacao.CREDITO)
        self.assertEqual(reversal, TipoTransacao.DEBITO)

    def test_filter_transactions_by_period(self):
        """Testa filtro de transações por período"""
        transactions = [
            Transacao(
                id='1', descricao='Compra 1', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-05T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            ),
            Transacao(
                id='2', descricao='Compra 2', valor=200.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-04-05T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            ),
            Transacao(
                id='3', descricao='Compra 3', valor=300.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-25T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            )
        ]
        
        # Filtrar março de 2024
        march_transactions = TransactionDomain.filter_transactions_by_period(transactions, 2024, 3)
        
        self.assertEqual(len(march_transactions), 2)  # Apenas transações de março

    def test_generate_transaction_id(self):
        """Testa geração de ID único"""
        id1 = TransactionDomain.generate_transaction_id()
        id2 = TransactionDomain.generate_transaction_id()
        
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        self.assertNotEqual(id1, id2)
        self.assertTrue(len(id1) > 30)  # UUID tem mais de 30 caracteres

    def test_prepare_transaction_creation_data(self):
        """Testa preparação de dados para criação"""
        data = TransactionDomain.prepare_transaction_creation_data(
            descricao='  Compra Teste  ',  # Com espaços
            valor=300.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao='2024-03-10T10:00:00',
            categoria='Alimentação',
            cartao_id='card123',
            parcelas=3,
            observacoes='Teste',
            compartilhado_com_alzi=True
        )
        
        self.assertEqual(data['descricao'], 'Compra Teste')  # Espaços removidos
        self.assertEqual(data['valor'], 300.0)
        self.assertEqual(data['tipo'], TipoTransacao.DEBITO)
        self.assertEqual(data['categoria'], 'Alimentação')
        self.assertEqual(data['cartao_id'], 'card123')
        self.assertEqual(len(data['parcelamento']), 3)  # Parcelamento calculado
        self.assertEqual(data['status'], StatusTransacao.PROCESSADA)  # Regra: inicia processada
        self.assertTrue(data['compartilhado_com_alzi'])
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_can_transaction_be_deleted_valid(self):
        """Testa se transação válida pode ser excluída"""
        transaction = Transacao(
            id='1', descricao='Compra', valor=100.0, tipo=TipoTransacao.DEBITO,
            data_transacao='2024-03-10T10:00:00', categoria=None, conta_id=None,
            cartao_id='card123', parcelamento=[], observacoes=None,
            status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
        )
        
        result = TransactionDomain.can_transaction_be_deleted(transaction)
        
        self.assertTrue(result['can_delete'])
        self.assertEqual(result['reason'], '')

    def test_can_transaction_be_deleted_cancelled(self):
        """Testa se transação cancelada pode ser excluída"""
        transaction = Transacao(
            id='1', descricao='Compra', valor=100.0, tipo=TipoTransacao.DEBITO,
            data_transacao='2024-03-10T10:00:00', categoria=None, conta_id=None,
            cartao_id='card123', parcelamento=[], observacoes=None,
            status=StatusTransacao.CANCELADA, compartilhado_com_alzi=False
        )
        
        result = TransactionDomain.can_transaction_be_deleted(transaction)
        
        self.assertFalse(result['can_delete'])
        self.assertIn('já está cancelada', result['reason'])

    def test_calculate_transaction_impact_account_debito(self):
        """Testa cálculo de impacto para débito em conta"""
        impact = TransactionDomain.calculate_transaction_impact(
            100.0, TipoTransacao.DEBITO, account_balance=1000.0
        )
        
        self.assertEqual(impact['account_balance_change'], -100.0)
        self.assertEqual(impact['new_account_balance'], 900.0)

    def test_calculate_transaction_impact_card_debito(self):
        """Testa cálculo de impacto para débito em cartão"""
        impact = TransactionDomain.calculate_transaction_impact(
            100.0, TipoTransacao.DEBITO, card_available_limit=5000.0
        )
        
        self.assertEqual(impact['card_limit_change'], -100.0)
        self.assertEqual(impact['new_card_available_limit'], 4900.0)

    def test_group_transactions_by_invoice(self):
        """Testa agrupamento de transações por fatura"""
        transactions = [
            Transacao(
                id='1', descricao='Compra 1', valor=100.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-03T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            ),
            Transacao(
                id='2', descricao='Compra 2', valor=200.0, tipo=TipoTransacao.DEBITO,
                data_transacao='2024-03-10T10:00:00', categoria=None, conta_id=None,
                cartao_id='card123', parcelamento=[], observacoes=None,
                status=StatusTransacao.PROCESSADA, compartilhado_com_alzi=False
            )
        ]
        
        grouped = TransactionDomain.group_transactions_by_invoice(transactions, 5)
        
        # Primeira transação (03/03) vai para fatura 2024-04
        # Segunda transação (10/03) vai para fatura 2024-05
        self.assertIn('2024-04', grouped)
        self.assertIn('2024-05', grouped)
        self.assertEqual(len(grouped['2024-04']), 1)
        self.assertEqual(len(grouped['2024-05']), 1)


if __name__ == '__main__':
    unittest.main()