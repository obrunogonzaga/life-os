"""
Testes unitários para CardDomain

Testa todas as regras de negócio relacionadas a cartões de crédito,
incluindo limites, datas de vencimento e cálculos de fatura.
"""

import unittest
from datetime import datetime, date
from decimal import Decimal

# Adicionar caminho para imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.domains import CardDomain
from utils.finance_models import CartaoCredito, BandeiraCartao


class TestCardDomain(unittest.TestCase):
    """Testes para CardDomain"""

    def setUp(self):
        """Setup para cada teste"""
        self.valid_card_data = {
            'nome': 'Cartão Teste',
            'banco': 'Banco Teste',
            'bandeira': BandeiraCartao.VISA,
            'limite': 5000.0,
            'dia_vencimento': 10,
            'dia_fechamento': 5
        }

    def test_validate_card_data_valid(self):
        """Testa validação com dados válidos"""
        result = CardDomain.validate_card_data(**self.valid_card_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_validate_card_data_invalid_nome(self):
        """Testa validação com nome inválido"""
        data = self.valid_card_data.copy()
        data['nome'] = 'A'  # Muito curto
        
        result = CardDomain.validate_card_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Nome do cartão deve ter pelo menos 2 caracteres', result['errors'])

    def test_validate_card_data_invalid_limite(self):
        """Testa validação com limite inválido"""
        data = self.valid_card_data.copy()
        data['limite'] = 0.0  # Zero
        
        result = CardDomain.validate_card_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Limite do cartão deve ser maior que zero', result['errors'])

    def test_validate_card_data_invalid_due_date(self):
        """Testa validação com dia de vencimento inválido"""
        data = self.valid_card_data.copy()
        data['dia_vencimento'] = 35  # Inválido
        
        result = CardDomain.validate_card_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Dia de vencimento deve estar entre 1 e 31', result['errors'])

    def test_validate_card_data_invalid_closing_date(self):
        """Testa validação com dia de fechamento inválido"""
        data = self.valid_card_data.copy()
        data['dia_fechamento'] = 0  # Inválido
        
        result = CardDomain.validate_card_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Dia de fechamento deve estar entre 1 e 31', result['errors'])

    def test_validate_card_data_same_dates(self):
        """Testa validação com datas iguais"""
        data = self.valid_card_data.copy()
        data['dia_vencimento'] = 5
        data['dia_fechamento'] = 5  # Iguais
        
        result = CardDomain.validate_card_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Dia de vencimento deve ser diferente do dia de fechamento', result['errors'])

    def test_validate_due_date_valid(self):
        """Testa validação de dia de vencimento válido"""
        self.assertTrue(CardDomain.validate_due_date(1))
        self.assertTrue(CardDomain.validate_due_date(15))
        self.assertTrue(CardDomain.validate_due_date(31))

    def test_validate_due_date_invalid(self):
        """Testa validação de dia de vencimento inválido"""
        self.assertFalse(CardDomain.validate_due_date(0))
        self.assertFalse(CardDomain.validate_due_date(32))
        self.assertFalse(CardDomain.validate_due_date(-1))

    def test_validate_closing_date_valid(self):
        """Testa validação de dia de fechamento válido"""
        self.assertTrue(CardDomain.validate_closing_date(1))
        self.assertTrue(CardDomain.validate_closing_date(15))
        self.assertTrue(CardDomain.validate_closing_date(31))

    def test_validate_closing_date_invalid(self):
        """Testa validação de dia de fechamento inválido"""
        self.assertFalse(CardDomain.validate_closing_date(0))
        self.assertFalse(CardDomain.validate_closing_date(32))
        self.assertFalse(CardDomain.validate_closing_date(-1))

    def test_calculate_available_limit_after_purchase(self):
        """Testa cálculo de limite após compra"""
        new_limit = CardDomain.calculate_available_limit_after_purchase(5000.0, 300.0)
        
        self.assertEqual(new_limit, 4700.0)

    def test_calculate_available_limit_after_purchase_exceeds(self):
        """Testa cálculo quando compra excede limite"""
        new_limit = CardDomain.calculate_available_limit_after_purchase(300.0, 500.0)
        
        self.assertEqual(new_limit, 0.0)  # Não pode ser negativo

    def test_calculate_available_limit_precision(self):
        """Testa precisão do cálculo de limite"""
        new_limit = CardDomain.calculate_available_limit_after_purchase(1000.0, 33.33)
        
        self.assertEqual(new_limit, 966.67)

    def test_restore_available_limit_after_cancellation(self):
        """Testa restauração de limite após cancelamento"""
        new_limit = CardDomain.restore_available_limit_after_cancellation(4700.0, 5000.0, 300.0)
        
        self.assertEqual(new_limit, 5000.0)

    def test_restore_available_limit_exceeds_total(self):
        """Testa restauração que excederia o limite total"""
        new_limit = CardDomain.restore_available_limit_after_cancellation(4800.0, 5000.0, 300.0)
        
        self.assertEqual(new_limit, 5000.0)  # Não pode exceder o total

    def test_can_make_purchase_valid(self):
        """Testa se pode fazer compra válida"""
        result = CardDomain.can_make_purchase(1000.0, 500.0)
        
        self.assertTrue(result['can_purchase'])
        self.assertEqual(result['message'], '')

    def test_can_make_purchase_insufficient_limit(self):
        """Testa compra com limite insuficiente"""
        result = CardDomain.can_make_purchase(300.0, 500.0)
        
        self.assertFalse(result['can_purchase'])
        self.assertIn('Limite insuficiente', result['message'])

    def test_can_make_purchase_invalid_value(self):
        """Testa compra com valor inválido"""
        result = CardDomain.can_make_purchase(1000.0, 0.0)
        
        self.assertFalse(result['can_purchase'])
        self.assertIn('Valor da compra deve ser maior que zero', result['message'])

    def test_calculate_invoice_period(self):
        """Testa cálculo de período de fatura"""
        start_date, end_date = CardDomain.calculate_invoice_period(5, 3, 2024)
        
        # Período: 05/02 a 05/03
        self.assertEqual(start_date, date(2024, 2, 5))
        self.assertEqual(end_date, date(2024, 3, 5))

    def test_calculate_invoice_period_february(self):
        """Testa período de fatura com fevereiro"""
        start_date, end_date = CardDomain.calculate_invoice_period(31, 3, 2024)
        
        # 31 de fevereiro não existe, deve ajustar para 29 (2024 é bissexto)
        self.assertEqual(start_date, date(2024, 2, 29))
        self.assertEqual(end_date, date(2024, 3, 31))

    def test_determine_invoice_month_for_transaction_before_closing(self):
        """Testa determinação de fatura para transação antes do fechamento"""
        # Transação em 03/03, fechamento dia 05
        invoice_month, invoice_year = CardDomain.determine_invoice_month_for_transaction(
            date(2024, 3, 3), 5
        )
        
        # Deve ir para fatura de março
        self.assertEqual(invoice_month, 3)
        self.assertEqual(invoice_year, 2024)

    def test_determine_invoice_month_for_transaction_after_closing(self):
        """Testa determinação de fatura para transação após o fechamento"""
        # Transação em 10/03, fechamento dia 05
        invoice_month, invoice_year = CardDomain.determine_invoice_month_for_transaction(
            date(2024, 3, 10), 5
        )
        
        # Deve ir para fatura de abril
        self.assertEqual(invoice_month, 4)
        self.assertEqual(invoice_year, 2024)

    def test_determine_invoice_month_december_transition(self):
        """Testa transição de dezembro para janeiro"""
        # Transação em 10/12, fechamento dia 05
        invoice_month, invoice_year = CardDomain.determine_invoice_month_for_transaction(
            date(2024, 12, 10), 5
        )
        
        # Deve ir para fatura de janeiro do próximo ano
        self.assertEqual(invoice_month, 1)
        self.assertEqual(invoice_year, 2025)

    def test_calculate_cards_summary(self):
        """Testa cálculo de resumo de cartões"""
        cards = [
            CartaoCredito(
                id='1', nome='Cartão 1', banco='Banco', bandeira=BandeiraCartao.VISA,
                limite=5000.0, limite_disponivel=4000.0, conta_vinculada_id=None,
                dia_vencimento=10, dia_fechamento=5, compartilhado_com_alzi=True, ativo=True
            ),
            CartaoCredito(
                id='2', nome='Cartão 2', banco='Banco', bandeira=BandeiraCartao.MASTERCARD,
                limite=3000.0, limite_disponivel=3000.0, conta_vinculada_id=None,
                dia_vencimento=15, dia_fechamento=10, compartilhado_com_alzi=False, ativo=True
            ),
            CartaoCredito(
                id='3', nome='Cartão 3', banco='Banco', bandeira=BandeiraCartao.VISA,
                limite=2000.0, limite_disponivel=1500.0, conta_vinculada_id=None,
                dia_vencimento=20, dia_fechamento=15, compartilhado_com_alzi=True, ativo=False  # Inativo
            )
        ]
        
        summary = CardDomain.calculate_cards_summary(cards)
        
        self.assertEqual(summary['total_cards'], 2)  # Apenas ativos
        self.assertEqual(summary['total_limit'], 8000.0)
        self.assertEqual(summary['total_available'], 7000.0)
        self.assertEqual(summary['used_limit'], 1000.0)
        self.assertEqual(summary['usage_percentage'], 12.5)
        self.assertEqual(summary['shared_cards_count'], 1)
        self.assertEqual(summary['inactive_cards'], 1)
        
        # Verificar estatísticas por bandeira
        self.assertIn('visa', summary['brands_stats'])
        self.assertIn('mastercard', summary['brands_stats'])
        self.assertEqual(summary['brands_stats']['visa']['count'], 1)  # Apenas ativo
        self.assertEqual(summary['brands_stats']['mastercard']['count'], 1)

    def test_generate_card_id(self):
        """Testa geração de ID único"""
        id1 = CardDomain.generate_card_id()
        id2 = CardDomain.generate_card_id()
        
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        self.assertNotEqual(id1, id2)
        self.assertTrue(len(id1) > 30)  # UUID tem mais de 30 caracteres

    def test_prepare_card_creation_data(self):
        """Testa preparação de dados para criação"""
        data = CardDomain.prepare_card_creation_data(
            nome='  Cartão Teste  ',  # Com espaços
            banco='Banco Teste',
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            conta_vinculada_id='conta123',
            compartilhado_com_alzi=True
        )
        
        self.assertEqual(data['nome'], 'Cartão Teste')  # Espaços removidos
        self.assertEqual(data['limite'], 5000.0)
        self.assertEqual(data['limite_disponivel'], 5000.0)  # Regra: igual ao limite
        self.assertTrue(data['ativo'])  # Regra: sempre ativo
        self.assertTrue(data['compartilhado_com_alzi'])
        self.assertEqual(data['conta_vinculada_id'], 'conta123')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_can_card_be_deleted_with_transactions(self):
        """Testa se cartão com transações pode ser excluído"""
        card = CartaoCredito(
            id='test', nome='Teste', banco='Banco', bandeira=BandeiraCartao.VISA,
            limite=5000.0, limite_disponivel=5000.0, conta_vinculada_id=None,
            dia_vencimento=10, dia_fechamento=5, compartilhado_com_alzi=False, ativo=True
        )
        
        result = CardDomain.can_card_be_deleted(card, has_transactions=True)
        
        self.assertFalse(result['can_delete'])
        self.assertIn('transações', result['reason'])

    def test_can_card_be_deleted_with_used_limit(self):
        """Testa se cartão com limite usado pode ser excluído"""
        card = CartaoCredito(
            id='test', nome='Teste', banco='Banco', bandeira=BandeiraCartao.VISA,
            limite=5000.0, limite_disponivel=4000.0, conta_vinculada_id=None,  # Limite usado
            dia_vencimento=10, dia_fechamento=5, compartilhado_com_alzi=False, ativo=True
        )
        
        result = CardDomain.can_card_be_deleted(card, has_transactions=False)
        
        self.assertFalse(result['can_delete'])
        self.assertIn('limite utilizado', result['reason'])

    def test_can_card_be_deleted_valid(self):
        """Testa se cartão válido pode ser excluído"""
        card = CartaoCredito(
            id='test', nome='Teste', banco='Banco', bandeira=BandeiraCartao.VISA,
            limite=5000.0, limite_disponivel=5000.0, conta_vinculada_id=None,
            dia_vencimento=10, dia_fechamento=5, compartilhado_com_alzi=False, ativo=True
        )
        
        result = CardDomain.can_card_be_deleted(card, has_transactions=False)
        
        self.assertTrue(result['can_delete'])
        self.assertEqual(result['reason'], '')

    def test_filter_cards_by_criteria(self):
        """Testa filtros de cartões"""
        cards = [
            CartaoCredito(
                id='1', nome='Cartão 1', banco='Banco', bandeira=BandeiraCartao.VISA,
                limite=5000.0, limite_disponivel=4000.0, conta_vinculada_id=None,
                dia_vencimento=10, dia_fechamento=5, compartilhado_com_alzi=True, ativo=True
            ),
            CartaoCredito(
                id='2', nome='Cartão 2', banco='Banco', bandeira=BandeiraCartao.MASTERCARD,
                limite=3000.0, limite_disponivel=3000.0, conta_vinculada_id=None,
                dia_vencimento=15, dia_fechamento=10, compartilhado_com_alzi=False, ativo=True
            ),
            CartaoCredito(
                id='3', nome='Cartão 3', banco='Banco', bandeira=BandeiraCartao.VISA,
                limite=2000.0, limite_disponivel=1500.0, conta_vinculada_id=None,
                dia_vencimento=20, dia_fechamento=15, compartilhado_com_alzi=True, ativo=False
            )
        ]
        
        # Filtrar apenas ativos
        ativos = CardDomain.filter_cards_by_criteria(cards, ativos_apenas=True)
        self.assertEqual(len(ativos), 2)
        
        # Filtrar apenas compartilhados
        compartilhados = CardDomain.filter_cards_by_criteria(
            cards, ativos_apenas=False, compartilhados_apenas=True
        )
        self.assertEqual(len(compartilhados), 2)
        
        # Filtrar por bandeira
        visa_cards = CardDomain.filter_cards_by_criteria(
            cards, ativos_apenas=False, bandeira=BandeiraCartao.VISA
        )
        self.assertEqual(len(visa_cards), 2)


if __name__ == '__main__':
    unittest.main()