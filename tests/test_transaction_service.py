"""
Testes unitários para TransactionService

Testa toda a lógica de negócios relacionada ao gerenciamento de transações financeiras.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.services.transaction_service import TransactionService
from utils.finance_models import (
    Transacao, Parcelamento, TipoTransacao, StatusTransacao, 
    ContaCorrente, CartaoCredito, TipoConta, BandeiraCartao
)


class TestTransactionService(unittest.TestCase):
    """Testes para TransactionService"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Mock do DatabaseManager
        self.mock_db_manager = Mock()
        
        # Mock do TransactionDomain
        with patch('modules.finances.services.transaction_service.TransactionDomain') as mock_domain_class:
            self.mock_transaction_domain = Mock()
            mock_domain_class.return_value = self.mock_transaction_domain
            
            # Criar service com mocks
            self.transaction_service = TransactionService(self.mock_db_manager)
    
    def test_create_transaction_success(self):
        """Testa criação bem-sucedida de transação simples"""
        # Arrange
        transacao_mock = Transacao(
            id="test-id",
            descricao="Compra Teste",
            valor=100.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao="2024-01-01",
            categoria="Alimentação",
            conta_id="conta-id",
            cartao_id=None,
            parcelamento=[],
            observacoes=None,
            status=StatusTransacao.PROCESSADA,
            compartilhado_com_alzi=False,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        self.mock_transaction_domain.create_transaction.return_value = transacao_mock
        
        # Mock dos services de validação
        with patch('modules.finances.services.transaction_service.AccountService') as mock_account_service_class:
            mock_account_service = Mock()
            mock_account_service_class.return_value = mock_account_service
            mock_account_service.get_account_by_id.return_value = Mock()  # Conta existe
            mock_account_service.update_balance.return_value = True
            
            # Act
            resultado = self.transaction_service.create_transaction(
                descricao="Compra Teste",
                valor=100.0,
                tipo=TipoTransacao.DEBITO,
                data_transacao="2024-01-01",
                categoria="Alimentação",
                conta_id="conta-id"
            )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.descricao, "Compra Teste")
        self.assertEqual(resultado.valor, 100.0)
        self.mock_transaction_domain.create_transaction.assert_called_once()
    
    def test_create_transaction_with_installments(self):
        """Testa criação de transação parcelada"""
        # Arrange
        parcelamento_mock = [
            Parcelamento(numero_parcela=1, total_parcelas=3, valor_parcela=100.0, data_vencimento="2024-01-01"),
            Parcelamento(numero_parcela=2, total_parcelas=3, valor_parcela=100.0, data_vencimento="2024-02-01"),
            Parcelamento(numero_parcela=3, total_parcelas=3, valor_parcela=100.0, data_vencimento="2024-03-01")
        ]
        
        transacao_mock = Transacao(
            id="test-id",
            descricao="Compra Parcelada",
            valor=300.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao="2024-01-01",
            categoria="Compras",
            conta_id=None,
            cartao_id="cartao-id",
            parcelamento=parcelamento_mock,
            observacoes=None,
            status=StatusTransacao.PROCESSADA,
            compartilhado_com_alzi=False
        )
        
        self.mock_transaction_domain.create_transaction.return_value = transacao_mock
        
        # Mock dos services de validação
        with patch('modules.finances.services.transaction_service.CardService') as mock_card_service_class:
            mock_card_service = Mock()
            mock_card_service_class.return_value = mock_card_service
            mock_card_service.get_card_by_id.return_value = Mock()  # Cartão existe
            mock_card_service.update_available_limit.return_value = True
            
            # Act
            resultado = self.transaction_service.create_transaction(
                descricao="Compra Parcelada",
                valor=300.0,
                tipo=TipoTransacao.DEBITO,
                data_transacao="2024-01-01",
                categoria="Compras",
                cartao_id="cartao-id",
                parcelas=3
            )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(len(resultado.parcelamento), 3)
        self.assertEqual(resultado.parcelamento[0].valor_parcela, 100.0)
    
    def test_create_transaction_invalid_description(self):
        """Testa criação de transação com descrição inválida"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.create_transaction(
                descricao="",  # Descrição vazia
                valor=100.0,
                tipo=TipoTransacao.DEBITO,
                data_transacao="2024-01-01",
                conta_id="conta-id"
            )
        
        self.assertIn("Descrição da transação é obrigatória", str(context.exception))
    
    def test_create_transaction_invalid_value(self):
        """Testa criação de transação com valor inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.create_transaction(
                descricao="Teste",
                valor=0.0,  # Valor zero
                tipo=TipoTransacao.DEBITO,
                data_transacao="2024-01-01",
                conta_id="conta-id"
            )
        
        self.assertIn("Valor deve ser maior que zero", str(context.exception))
    
    def test_create_transaction_invalid_date(self):
        """Testa criação de transação com data inválida"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.create_transaction(
                descricao="Teste",
                valor=100.0,
                tipo=TipoTransacao.DEBITO,
                data_transacao="data-invalida",  # Data inválida
                conta_id="conta-id"
            )
        
        self.assertIn("Formato de data inválido", str(context.exception))
    
    def test_create_transaction_no_account_or_card(self):
        """Testa criação de transação sem conta nem cartão"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.create_transaction(
                descricao="Teste",
                valor=100.0,
                tipo=TipoTransacao.DEBITO,
                data_transacao="2024-01-01"
                # Sem conta_id nem cartao_id
            )
        
        self.assertIn("Deve ser informada uma conta ou um cartão", str(context.exception))
    
    def test_create_transaction_both_account_and_card(self):
        """Testa criação de transação com conta e cartão simultaneamente"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.create_transaction(
                descricao="Teste",
                valor=100.0,
                tipo=TipoTransacao.DEBITO,
                data_transacao="2024-01-01",
                conta_id="conta-id",
                cartao_id="cartao-id"  # Ambos informados
            )
        
        self.assertIn("Não é possível associar a transação a conta e cartão simultaneamente", str(context.exception))
    
    def test_create_transaction_invalid_installments_for_credit(self):
        """Testa parcelamento inválido para crédito em cartão"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.create_transaction(
                descricao="Teste",
                valor=100.0,
                tipo=TipoTransacao.CREDITO,  # Crédito
                data_transacao="2024-01-01",
                cartao_id="cartao-id",
                parcelas=3  # Parcelado
            )
        
        self.assertIn("Apenas débitos podem ser parcelados", str(context.exception))
    
    def test_get_transactions_by_month_valid(self):
        """Testa obtenção de transações por mês válido"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Transação 1", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", conta_id="conta-id"),
            Transacao(id="2", descricao="Transação 2", valor=200, tipo=TipoTransacao.CREDITO, 
                     data_transacao="2024-01-20", conta_id="conta-id")
        ]
        
        self.mock_transaction_domain.list_transactions.return_value = transacoes_mock
        
        # Act
        resultado = self.transaction_service.get_transactions_by_month(2024, 1)
        
        # Assert
        self.assertEqual(len(resultado), 2)
        self.mock_transaction_domain.list_transactions.assert_called_once()
        
        # Verificar se o filtro de data foi aplicado corretamente
        call_args = self.mock_transaction_domain.list_transactions.call_args[0][0]
        self.assertIn("data_transacao", call_args)
        self.assertEqual(call_args["data_transacao"]["$gte"], "2024-01-01")
        self.assertEqual(call_args["data_transacao"]["$lt"], "2024-02-01")
    
    def test_get_transactions_by_month_invalid_month(self):
        """Testa obtenção de transações com mês inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.get_transactions_by_month(2024, 13)  # Mês inválido
        
        self.assertIn("Mês deve estar entre 1 e 12", str(context.exception))
    
    def test_get_transactions_by_month_invalid_year(self):
        """Testa obtenção de transações com ano inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.get_transactions_by_month(1800, 1)  # Ano inválido
        
        self.assertIn("Ano deve estar entre 1900 e 2100", str(context.exception))
    
    def test_get_transactions_by_month_shared_only(self):
        """Testa obtenção apenas de transações compartilhadas"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Transação Compartilhada", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", conta_id="conta-id", compartilhado_com_alzi=True)
        ]
        
        self.mock_transaction_domain.list_transactions.return_value = transacoes_mock
        
        # Act
        resultado = self.transaction_service.get_transactions_by_month(2024, 1, shared_only=True)
        
        # Assert
        self.assertEqual(len(resultado), 1)
        
        # Verificar se o filtro de compartilhamento foi aplicado
        call_args = self.mock_transaction_domain.list_transactions.call_args[0][0]
        self.assertTrue(call_args["compartilhado_com_alzi"])
    
    def test_update_transaction_success(self):
        """Testa atualização bem-sucedida de transação"""
        # Arrange
        transacao_existente = Transacao(
            id="test-id",
            descricao="Descrição Original",
            valor=100.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao="2024-01-01",
            conta_id="conta-id",
            parcelamento=[],
            status=StatusTransacao.PROCESSADA,
            compartilhado_com_alzi=False
        )
        
        self.mock_transaction_domain.get_transaction_by_id.return_value = transacao_existente
        self.mock_transaction_domain.update_transaction.return_value = True
        
        # Act
        resultado = self.transaction_service.update_transaction("test-id", descricao="Nova Descrição")
        
        # Assert
        self.assertTrue(resultado)
        self.mock_transaction_domain.update_transaction.assert_called_once()
    
    def test_update_transaction_not_found(self):
        """Testa atualização de transação inexistente"""
        # Arrange
        self.mock_transaction_domain.get_transaction_by_id.return_value = None
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.update_transaction("invalid-id", descricao="Nova Descrição")
        
        self.assertIn("Transação não encontrada", str(context.exception))
    
    def test_delete_transaction_success(self):
        """Testa exclusão bem-sucedida de transação"""
        # Arrange
        transacao_existente = Transacao(
            id="test-id",
            descricao="Transação para Excluir",
            valor=100.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao="2024-01-01",
            conta_id="conta-id",
            parcelamento=[],
            status=StatusTransacao.PROCESSADA,
            compartilhado_com_alzi=False
        )
        
        self.mock_transaction_domain.get_transaction_by_id.return_value = transacao_existente
        self.mock_transaction_domain.delete_transaction.return_value = True
        
        # Mock do AccountService para reversão
        with patch('modules.finances.services.transaction_service.AccountService') as mock_account_service_class:
            mock_account_service = Mock()
            mock_account_service_class.return_value = mock_account_service
            mock_account_service.update_balance.return_value = True
            
            # Act
            resultado = self.transaction_service.delete_transaction("test-id")
        
        # Assert
        self.assertTrue(resultado)
        self.mock_transaction_domain.delete_transaction.assert_called_once_with("test-id")
        
        # Verificar se a reversão do saldo foi chamada
        mock_account_service.update_balance.assert_called_once_with("conta-id", 100.0, TipoTransacao.CREDITO)
    
    def test_delete_multiple_transactions_success(self):
        """Testa exclusão múltipla bem-sucedida"""
        # Arrange
        transaction_ids = ["id1", "id2", "id3"]
        
        # Mock para cada exclusão individual
        with patch.object(self.transaction_service, 'delete_transaction', return_value=True):
            # Act
            resultado = self.transaction_service.delete_multiple_transactions(transaction_ids)
        
        # Assert
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['total_requested'], 3)
        self.assertEqual(resultado['deleted'], 3)
        self.assertEqual(len(resultado['errors']), 0)
    
    def test_delete_multiple_transactions_partial_failure(self):
        """Testa exclusão múltipla com falhas parciais"""
        # Arrange
        transaction_ids = ["id1", "id2", "id3"]
        
        def mock_delete(transaction_id):
            if transaction_id == "id2":
                return False  # Falha na segunda transação
            return True
        
        # Mock para simular falha parcial
        with patch.object(self.transaction_service, 'delete_transaction', side_effect=mock_delete):
            # Act
            resultado = self.transaction_service.delete_multiple_transactions(transaction_ids)
        
        # Assert
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['total_requested'], 3)
        self.assertEqual(resultado['deleted'], 2)
        self.assertEqual(len(resultado['errors']), 1)
    
    def test_get_transactions_summary(self):
        """Testa geração de resumo de transações"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Débito 1", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-01", categoria="Alimentação", compartilhado_com_alzi=True),
            Transacao(id="2", descricao="Débito 2", valor=200, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-02", categoria="Transporte", compartilhado_com_alzi=False),
            Transacao(id="3", descricao="Crédito 1", valor=150, tipo=TipoTransacao.CREDITO, 
                     data_transacao="2024-01-03", categoria="Salário", compartilhado_com_alzi=False)
        ]
        
        self.mock_transaction_domain.list_transactions.return_value = transacoes_mock
        
        # Act
        resumo = self.transaction_service.get_transactions_summary()
        
        # Assert
        self.assertEqual(resumo['total_transactions'], 3)
        self.assertEqual(resumo['total_debits'], 300.0)  # 100 + 200
        self.assertEqual(resumo['total_credits'], 150.0)
        self.assertEqual(resumo['balance'], -150.0)  # 150 - 300
        self.assertEqual(resumo['shared_expenses'], 100.0)  # Apenas o primeiro débito
        self.assertIn('transactions_by_category', resumo)
        self.assertIn('transactions_by_type', resumo)
    
    def test_generate_installments_simple(self):
        """Testa geração de parcelamento simples"""
        # Act
        parcelamento = self.transaction_service._generate_installments(300.0, 3, "2024-01-01")
        
        # Assert
        self.assertEqual(len(parcelamento), 3)
        self.assertEqual(parcelamento[0].numero_parcela, 1)
        self.assertEqual(parcelamento[0].total_parcelas, 3)
        self.assertEqual(parcelamento[0].valor_parcela, 100.0)
        self.assertEqual(parcelamento[1].numero_parcela, 2)
        self.assertEqual(parcelamento[2].numero_parcela, 3)
    
    def test_generate_installments_single(self):
        """Testa que não gera parcelamento para parcela única"""
        # Act
        parcelamento = self.transaction_service._generate_installments(100.0, 1, "2024-01-01")
        
        # Assert
        self.assertEqual(len(parcelamento), 0)


if __name__ == '__main__':
    unittest.main()