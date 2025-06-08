"""
Testes unitários para PeriodService

Testa toda a lógica de negócios relacionada ao gerenciamento de períodos e faturas.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.services.period_service import PeriodService
from utils.finance_models import CartaoCredito, Transacao, TipoTransacao, BandeiraCartao


class TestPeriodService(unittest.TestCase):
    """Testes para PeriodService"""
    
    def setUp(self):
        """Configuração para cada teste"""
        self.mock_db_manager = Mock()
        
        with patch('modules.finances.services.period_service.PeriodDomain') as mock_domain_class:
            self.mock_period_domain = Mock()
            mock_domain_class.return_value = self.mock_period_domain
            
            self.period_service = PeriodService(self.mock_db_manager)
    
    @patch('modules.finances.services.period_service.CardService')
    def test_get_billing_period_transactions_success(self, mock_card_service_class):
        """Testa obtenção de transações de fatura com sucesso"""
        # Arrange
        cartao_mock = CartaoCredito(
            id="cartao-id",
            nome="Cartão Teste",
            banco="Banco",
            bandeira=BandeiraCartao.VISA,
            limite=5000,
            limite_disponivel=4000,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        transacoes_mock = [
            Transacao(id="1", descricao="Compra 1", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", cartao_id="cartao-id"),
            Transacao(id="2", descricao="Compra 2", valor=200, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-20", cartao_id="cartao-id")
        ]
        
        mock_card_service = Mock()
        mock_card_service_class.return_value = mock_card_service
        mock_card_service.get_card_by_id.return_value = cartao_mock
        
        self.mock_period_domain.get_billing_period_transactions.return_value = transacoes_mock
        
        # Act
        resultado = self.period_service.get_billing_period_transactions("cartao-id", 2, 2024)
        
        # Assert
        self.assertEqual(len(resultado), 2)
        mock_card_service.get_card_by_id.assert_called_once_with("cartao-id")
        self.mock_period_domain.get_billing_period_transactions.assert_called_once()
    
    def test_get_billing_period_transactions_invalid_month(self):
        """Testa obtenção de transações com mês inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.period_service.get_billing_period_transactions("cartao-id", 13, 2024)
        
        self.assertIn("Mês da fatura deve estar entre 1 e 12", str(context.exception))
    
    def test_get_billing_period_transactions_invalid_year(self):
        """Testa obtenção de transações com ano inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.period_service.get_billing_period_transactions("cartao-id", 1, 1800)
        
        self.assertIn("Ano da fatura deve estar entre 1900 e 2100", str(context.exception))
    
    @patch('modules.finances.services.period_service.CardService')
    def test_get_billing_period_transactions_card_not_found(self, mock_card_service_class):
        """Testa obtenção de transações com cartão inexistente"""
        # Arrange
        mock_card_service = Mock()
        mock_card_service_class.return_value = mock_card_service
        mock_card_service.get_card_by_id.return_value = None  # Cartão não encontrado
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.period_service.get_billing_period_transactions("invalid-id", 1, 2024)
        
        self.assertIn("Cartão não encontrado", str(context.exception))
    
    def test_get_monthly_summary_success(self):
        """Testa obtenção de resumo mensal"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Débito", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", conta_id="conta-id", compartilhado_com_alzi=True),
            Transacao(id="2", descricao="Crédito", valor=50, tipo=TipoTransacao.CREDITO, 
                     data_transacao="2024-01-20", conta_id="conta-id"),
            Transacao(id="3", descricao="Cartão", valor=200, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-25", cartao_id="cartao-id", compartilhado_com_alzi=False)
        ]
        
        with patch('modules.finances.services.period_service.TransactionService') as mock_trans_service_class:
            mock_trans_service = Mock()
            mock_trans_service_class.return_value = mock_trans_service
            mock_trans_service.get_transactions_by_month.return_value = transacoes_mock
            
            # Act
            resultado = self.period_service.get_monthly_summary(2024, 1)
        
        # Assert
        self.assertEqual(resultado['periodo'], "01/2024")
        self.assertEqual(resultado['total_transacoes'], 3)
        self.assertEqual(resultado['total_debitos'], 300.0)  # 100 + 200
        self.assertEqual(resultado['total_creditos'], 50.0)
        self.assertEqual(resultado['saldo_liquido'], -250.0)  # 50 - 300
        self.assertEqual(resultado['total_compartilhado'], 100.0)  # Apenas o primeiro
        self.assertEqual(resultado['valor_individual'], 50.0)  # 100 / 2
        self.assertEqual(resultado['transacoes_conta'], 2)
        self.assertEqual(resultado['transacoes_cartao'], 1)
    
    def test_get_monthly_summary_invalid_month(self):
        """Testa resumo mensal com mês inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.period_service.get_monthly_summary(2024, 0)
        
        self.assertIn("Mês deve estar entre 1 e 12", str(context.exception))
    
    def test_get_year_summary_success(self):
        """Testa obtenção de resumo anual"""
        # Mock para get_monthly_summary
        monthly_summaries = []
        for mes in range(1, 13):
            monthly_summaries.append({
                'periodo': f"{mes:02d}/2024",
                'total_transacoes': 2,
                'total_debitos': 100.0 * mes,  # Crescente
                'total_creditos': 50.0,
                'saldo_liquido': 50.0 - (100.0 * mes),
                'total_compartilhado': 50.0 * mes,
                'valor_individual': 25.0 * mes
            })
        
        with patch.object(self.period_service, 'get_monthly_summary', side_effect=monthly_summaries):
            # Act
            resultado = self.period_service.get_year_summary(2024)
        
        # Assert
        self.assertEqual(resultado['ano'], 2024)
        self.assertEqual(resultado['total_debitos'], 7800.0)  # Soma de 100*1 + 100*2 + ... + 100*12
        self.assertEqual(resultado['total_creditos'], 600.0)  # 50 * 12
        self.assertEqual(len(resultado['resumos_mensais']), 12)
        self.assertIn('melhor_mes', resultado)
        self.assertIn('pior_mes', resultado)
    
    @patch('modules.finances.services.period_service.CardService')
    def test_get_current_invoices_summary(self, mock_card_service_class):
        """Testa obtenção de resumo de faturas atuais"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=4000, dia_vencimento=10, dia_fechamento=5, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=2500, dia_vencimento=15, dia_fechamento=10, ativo=True)
        ]
        
        mock_card_service = Mock()
        mock_card_service_class.return_value = mock_card_service
        mock_card_service.list_cards.return_value = cartoes_mock
        
        # Mock para _get_current_invoice_info
        invoice_info_mock = {
            'cartao_id': '1',
            'cartao_nome': 'Cartão 1',
            'mes': 2,
            'ano': 2024,
            'total_valor': 1000.0,
            'total_compartilhado': 500.0,
            'percentual_uso': 20.0
        }
        
        with patch.object(self.period_service, '_get_current_invoice_info', return_value=invoice_info_mock):
            # Act
            resultado = self.period_service.get_current_invoices_summary()
        
        # Assert
        self.assertEqual(len(resultado), 2)  # Dois cartões processados
    
    def test_calculate_billing_dates(self):
        """Testa cálculo de datas de faturamento"""
        # Arrange
        cartao_mock = CartaoCredito(
            id="1",
            nome="Cartão Teste",
            banco="Banco",
            bandeira=BandeiraCartao.VISA,
            limite=5000,
            limite_disponivel=4000,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        expected_dates = {
            'periodo_inicio': '2024-01-06',
            'periodo_fim': '2024-02-05',
            'data_vencimento': '2024-02-10'
        }
        
        self.mock_period_domain.calculate_billing_dates.return_value = expected_dates
        
        # Act
        resultado = self.period_service.calculate_billing_dates(cartao_mock, 2, 2024)
        
        # Assert
        self.assertEqual(resultado, expected_dates)
        self.mock_period_domain.calculate_billing_dates.assert_called_once_with(cartao_mock, 2, 2024)


if __name__ == '__main__':
    unittest.main()