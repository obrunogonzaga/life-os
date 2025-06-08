"""
Testes unitários para AlziService

Testa toda a lógica de negócios relacionada ao gerenciamento de gastos compartilhados com Alzi.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.services.alzi_service import AlziService
from utils.finance_models import Transacao, TipoTransacao, ContaCorrente, CartaoCredito, BandeiraCartao


class TestAlziService(unittest.TestCase):
    """Testes para AlziService"""
    
    def setUp(self):
        """Configuração para cada teste"""
        self.mock_db_manager = Mock()
        
        with patch('modules.finances.services.alzi_service.AlziDomain') as mock_domain_class:
            self.mock_alzi_domain = Mock()
            mock_domain_class.return_value = self.mock_alzi_domain
            
            self.alzi_service = AlziService(self.mock_db_manager)
    
    def test_get_shared_transactions_summary_success(self):
        """Testa obtenção de resumo de transações compartilhadas"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Mercado", valor=200, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", conta_id="conta-id", compartilhado_com_alzi=True),
            Transacao(id="2", descricao="Restaurante", valor=150, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-20", cartao_id="cartao-id", compartilhado_com_alzi=True),
            Transacao(id="3", descricao="Transferência", valor=100, tipo=TipoTransacao.CREDITO, 
                     data_transacao="2024-01-25", conta_id="conta-id", compartilhado_com_alzi=True)
        ]
        
        self.mock_alzi_domain.get_shared_transactions_by_month.return_value = transacoes_mock
        
        # Act
        resultado = self.alzi_service.get_shared_transactions_summary(2024, 1)
        
        # Assert
        self.assertEqual(resultado['periodo'], "01/2024")
        self.assertEqual(resultado['total_transacoes'], 3)
        self.assertEqual(resultado['total_debitos'], 350.0)  # 200 + 150
        self.assertEqual(resultado['total_creditos'], 100.0)
        self.assertEqual(resultado['saldo_liquido_compartilhado'], -250.0)  # 100 - 350
        self.assertEqual(resultado['valor_individual'], 175.0)  # 350 / 2
        self.assertEqual(resultado['valor_bruno'], 175.0)
        self.assertEqual(resultado['valor_alzi'], 175.0)
        self.assertIn('transacoes_por_categoria', resultado)
        self.assertIn('transacoes_por_conta_cartao', resultado)
        self.assertIn('transacoes', resultado)
    
    def test_get_shared_transactions_summary_invalid_month(self):
        """Testa resumo com mês inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.alzi_service.get_shared_transactions_summary(2024, 13)
        
        self.assertIn("Mês deve estar entre 1 e 12", str(context.exception))
    
    def test_get_shared_transactions_summary_invalid_year(self):
        """Testa resumo com ano inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.alzi_service.get_shared_transactions_summary(1800, 1)
        
        self.assertIn("Ano deve estar entre 1900 e 2100", str(context.exception))
    
    @patch('modules.finances.services.alzi_service.datetime')
    def test_get_current_month_summary(self, mock_datetime):
        """Testa obtenção do resumo do mês atual"""
        # Arrange
        mock_datetime.now.return_value = datetime(2024, 3, 15)
        
        expected_summary = {
            'periodo': "03/2024",
            'total_debitos': 500.0,
            'valor_individual': 250.0
        }
        
        with patch.object(self.alzi_service, 'get_shared_transactions_summary', return_value=expected_summary):
            # Act
            resultado = self.alzi_service.get_current_month_summary()
        
        # Assert
        self.assertEqual(resultado['periodo'], "03/2024")
        self.assertEqual(resultado['total_debitos'], 500.0)
    
    def test_get_year_shared_summary_success(self):
        """Testa obtenção de resumo anual compartilhado"""
        # Mock para get_shared_transactions_summary
        monthly_summaries = []
        for mes in range(1, 13):
            monthly_summaries.append({
                'periodo': f"{mes:02d}/2024",
                'total_transacoes': 5,
                'total_debitos': 100.0 * mes,
                'total_creditos': 20.0,
                'saldo_liquido_compartilhado': 20.0 - (100.0 * mes),
                'valor_individual': 50.0 * mes
            })
        
        with patch.object(self.alzi_service, 'get_shared_transactions_summary', side_effect=monthly_summaries):
            # Act
            resultado = self.alzi_service.get_year_shared_summary(2024)
        
        # Assert
        self.assertEqual(resultado['ano'], 2024)
        self.assertEqual(resultado['total_debitos'], 7800.0)  # Soma de 100*1 + 100*2 + ... + 100*12
        self.assertEqual(resultado['total_creditos'], 240.0)  # 20 * 12
        self.assertEqual(resultado['valor_individual_ano'], 3900.0)  # 7800 / 2
        self.assertEqual(resultado['valor_bruno_ano'], 3900.0)
        self.assertEqual(resultado['valor_alzi_ano'], 3900.0)
        self.assertEqual(len(resultado['resumos_mensais']), 12)
        self.assertEqual(resultado['media_mensal'], 650.0)  # 7800 / 12
        self.assertIn('mes_maior_gasto', resultado)
        self.assertIn('mes_menor_gasto', resultado)
    
    @patch('modules.finances.services.alzi_service.AccountService')
    def test_get_shared_accounts_summary(self, mock_account_service_class):
        """Testa obtenção de resumo de contas compartilhadas"""
        # Arrange
        expected_summary = {
            'total_accounts': 2,
            'total_balance': 5000.0,
            'accounts_by_type': {'corrente': 1, 'poupanca': 1}
        }
        
        mock_account_service = Mock()
        mock_account_service_class.return_value = mock_account_service
        mock_account_service.get_shared_accounts_summary.return_value = expected_summary
        
        # Act
        resultado = self.alzi_service.get_shared_accounts_summary()
        
        # Assert
        self.assertEqual(resultado, expected_summary)
        mock_account_service.get_shared_accounts_summary.assert_called_once()
    
    @patch('modules.finances.services.alzi_service.CardService')
    def test_get_shared_cards_summary(self, mock_card_service_class):
        """Testa obtenção de resumo de cartões compartilhados"""
        # Arrange
        expected_summary = {
            'total_cards': 2,
            'total_limit': 8000.0,
            'available_limit': 6000.0,
            'cards_by_brand': {'visa': 1, 'mastercard': 1}
        }
        
        mock_card_service = Mock()
        mock_card_service_class.return_value = mock_card_service
        mock_card_service.get_shared_cards_summary.return_value = expected_summary
        
        # Act
        resultado = self.alzi_service.get_shared_cards_summary()
        
        # Assert
        self.assertEqual(resultado, expected_summary)
        mock_card_service.get_shared_cards_summary.assert_called_once()
    
    def test_get_comprehensive_shared_report(self):
        """Testa geração de relatório completo"""
        # Arrange
        transacoes_summary = {
            'periodo': "01/2024",
            'total_debitos': 1000.0,
            'valor_individual': 500.0,
            'transacoes_por_categoria': {'Alimentação': {'total': 600.0}},
            'transacoes_por_conta_cartao': {'contas': {}, 'cartoes': {}},
            'transacoes': []
        }
        
        accounts_summary = {'total_accounts': 1, 'total_balance': 2000.0}
        cards_summary = {'total_cards': 1, 'total_limit': 5000.0}
        
        with patch.object(self.alzi_service, 'get_shared_transactions_summary', return_value=transacoes_summary), \
             patch.object(self.alzi_service, 'get_shared_accounts_summary', return_value=accounts_summary), \
             patch.object(self.alzi_service, 'get_shared_cards_summary', return_value=cards_summary), \
             patch.object(self.alzi_service, '_compare_with_previous_month', return_value={'diferenca': 100.0}):
            
            # Act
            resultado = self.alzi_service.get_comprehensive_shared_report(2024, 1)
        
        # Assert
        self.assertEqual(resultado['periodo'], "01/2024")
        self.assertIn('resumo_geral', resultado)
        self.assertIn('contas_compartilhadas', resultado)
        self.assertIn('cartoes_compartilhados', resultado)
        self.assertIn('transacoes_detalhadas', resultado)
        self.assertIn('insights', resultado)
        self.assertIn('transacoes', resultado)
        
        self.assertEqual(resultado['resumo_geral']['total_gasto_compartilhado'], 1000.0)
        self.assertEqual(resultado['resumo_geral']['valor_individual'], 500.0)
    
    @patch('modules.finances.services.alzi_service.TransactionService')
    def test_mark_transaction_as_shared_success(self, mock_trans_service_class):
        """Testa marcação de transação como compartilhada"""
        # Arrange
        mock_trans_service = Mock()
        mock_trans_service_class.return_value = mock_trans_service
        mock_trans_service.update_transaction.return_value = True
        
        # Act
        resultado = self.alzi_service.mark_transaction_as_shared("transaction-id")
        
        # Assert
        self.assertTrue(resultado)
        mock_trans_service.update_transaction.assert_called_once_with("transaction-id", compartilhado_com_alzi=True)
    
    @patch('modules.finances.services.alzi_service.TransactionService')
    def test_unmark_transaction_as_shared_success(self, mock_trans_service_class):
        """Testa remoção de marcação de compartilhamento"""
        # Arrange
        mock_trans_service = Mock()
        mock_trans_service_class.return_value = mock_trans_service
        mock_trans_service.update_transaction.return_value = True
        
        # Act
        resultado = self.alzi_service.unmark_transaction_as_shared("transaction-id")
        
        # Assert
        self.assertTrue(resultado)
        mock_trans_service.update_transaction.assert_called_once_with("transaction-id", compartilhado_com_alzi=False)
    
    def test_bulk_mark_transactions_as_shared_success(self):
        """Testa marcação em lote bem-sucedida"""
        # Arrange
        transaction_ids = ["id1", "id2", "id3"]
        
        with patch.object(self.alzi_service, 'mark_transaction_as_shared', return_value=True):
            # Act
            resultado = self.alzi_service.bulk_mark_transactions_as_shared(transaction_ids)
        
        # Assert
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['total_requested'], 3)
        self.assertEqual(resultado['marked'], 3)
        self.assertEqual(len(resultado['errors']), 0)
    
    def test_bulk_mark_transactions_as_shared_partial_failure(self):
        """Testa marcação em lote com falhas parciais"""
        # Arrange
        transaction_ids = ["id1", "id2", "id3"]
        
        def mock_mark(transaction_id):
            if transaction_id == "id2":
                return False  # Falha na segunda
            return True
        
        with patch.object(self.alzi_service, 'mark_transaction_as_shared', side_effect=mock_mark):
            # Act
            resultado = self.alzi_service.bulk_mark_transactions_as_shared(transaction_ids)
        
        # Assert
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['total_requested'], 3)
        self.assertEqual(resultado['marked'], 2)
        self.assertEqual(len(resultado['errors']), 1)
    
    def test_calculate_settlement(self):
        """Testa cálculo de acerto de contas"""
        # Arrange
        resumo_mock = {
            'periodo': "01/2024",
            'total_debitos': 1000.0,
            'transacoes_por_categoria': {
                'Alimentação': {'total': 600.0},
                'Transporte': {'total': 400.0}
            }
        }
        
        with patch.object(self.alzi_service, 'get_shared_transactions_summary', return_value=resumo_mock):
            # Act
            resultado = self.alzi_service.calculate_settlement(2024, 1)
        
        # Assert
        self.assertEqual(resultado['periodo'], "01/2024")
        self.assertEqual(resultado['valor_total_gasto'], 1000.0)
        self.assertEqual(resultado['valor_bruno'], 500.0)
        self.assertEqual(resultado['valor_alzi'], 500.0)
        self.assertEqual(resultado['metodo_divisao'], '50/50')
        self.assertIn('observacoes', resultado)
        self.assertIn('detalhamento', resultado)


if __name__ == '__main__':
    unittest.main()