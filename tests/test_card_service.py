"""
Testes unitários para CardService

Testa toda a lógica de negócios relacionada ao gerenciamento de cartões de crédito.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.services.card_service import CardService
from utils.finance_models import CartaoCredito, BandeiraCartao, ContaCorrente, TipoConta


class TestCardService(unittest.TestCase):
    """Testes para CardService"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Mock do DatabaseManager
        self.mock_db_manager = Mock()
        
        # Mock do CardDomain
        with patch('modules.finances.services.card_service.CardDomain') as mock_domain_class:
            self.mock_card_domain = Mock()
            mock_domain_class.return_value = self.mock_card_domain
            
            # Criar service com mocks
            self.card_service = CardService(self.mock_db_manager)
    
    def test_create_card_success(self):
        """Testa criação bem-sucedida de cartão"""
        # Arrange
        cartao_mock = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            compartilhado_com_alzi=False,
            ativo=True,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        self.mock_card_domain.create_card.return_value = cartao_mock
        self.mock_card_domain.list_cards.return_value = []  # Nenhum cartão existente
        
        # Act
        resultado = self.card_service.create_card(
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            compartilhado_com_alzi=False
        )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nome, "Cartão Teste")
        self.assertEqual(resultado.banco, "Banco Teste")
        self.assertEqual(resultado.bandeira, BandeiraCartao.VISA)
        self.mock_card_domain.create_card.assert_called_once()
    
    def test_create_card_invalid_name(self):
        """Testa criação de cartão com nome inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.create_card(
                nome="",  # Nome vazio
                banco="Banco Teste",
                bandeira=BandeiraCartao.VISA,
                limite=5000.0,
                dia_vencimento=10,
                dia_fechamento=5
            )
        
        self.assertIn("Nome do cartão é obrigatório", str(context.exception))
    
    def test_create_card_invalid_limit(self):
        """Testa criação de cartão com limite inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.create_card(
                nome="Cartão Teste",
                banco="Banco Teste",
                bandeira=BandeiraCartao.VISA,
                limite=0.0,  # Limite zero
                dia_vencimento=10,
                dia_fechamento=5
            )
        
        self.assertIn("Limite deve ser maior que zero", str(context.exception))
    
    def test_create_card_invalid_due_date(self):
        """Testa criação de cartão com dia de vencimento inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.create_card(
                nome="Cartão Teste",
                banco="Banco Teste",
                bandeira=BandeiraCartao.VISA,
                limite=5000.0,
                dia_vencimento=32,  # Dia inválido
                dia_fechamento=5
            )
        
        self.assertIn("Dia de vencimento deve estar entre 1 e 31", str(context.exception))
    
    def test_create_card_same_dates(self):
        """Testa criação de cartão com vencimento e fechamento iguais"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.create_card(
                nome="Cartão Teste",
                banco="Banco Teste",
                bandeira=BandeiraCartao.VISA,
                limite=5000.0,
                dia_vencimento=10,
                dia_fechamento=10  # Mesmo dia do vencimento
            )
        
        self.assertIn("Dia de vencimento e fechamento não podem ser iguais", str(context.exception))
    
    @patch('modules.finances.services.card_service.AccountService')
    def test_create_card_with_linked_account(self, mock_account_service_class):
        """Testa criação de cartão com conta vinculada"""
        # Arrange
        mock_account_service = Mock()
        mock_account_service_class.return_value = mock_account_service
        
        conta_mock = ContaCorrente(
            id="account-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0
        )
        
        mock_account_service.get_account_by_id.return_value = conta_mock
        
        cartao_mock = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            conta_vinculada_id="account-id",
            ativo=True
        )
        
        self.mock_card_domain.create_card.return_value = cartao_mock
        self.mock_card_domain.list_cards.return_value = []
        
        # Act
        resultado = self.card_service.create_card(
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            conta_vinculada_id="account-id"
        )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.conta_vinculada_id, "account-id")
        mock_account_service.get_account_by_id.assert_called_once_with("account-id")
    
    @patch('modules.finances.services.card_service.AccountService')
    def test_create_card_with_invalid_linked_account(self, mock_account_service_class):
        """Testa criação de cartão com conta vinculada inexistente"""
        # Arrange
        mock_account_service = Mock()
        mock_account_service_class.return_value = mock_account_service
        mock_account_service.get_account_by_id.return_value = None  # Conta não encontrada
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.create_card(
                nome="Cartão Teste",
                banco="Banco Teste",
                bandeira=BandeiraCartao.VISA,
                limite=5000.0,
                dia_vencimento=10,
                dia_fechamento=5,
                conta_vinculada_id="invalid-id"
            )
        
        self.assertIn("Conta vinculada não encontrada", str(context.exception))
    
    def test_create_card_duplicate(self):
        """Testa criação de cartão duplicado"""
        # Arrange
        cartao_existente = CartaoCredito(
            id="existing-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_domain.list_cards.return_value = [cartao_existente]
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.create_card(
                nome="Cartão Teste",  # Mesmo nome
                banco="Banco Teste",  # Mesmo banco
                bandeira=BandeiraCartao.MASTERCARD,
                limite=3000.0,
                dia_vencimento=15,
                dia_fechamento=10
            )
        
        self.assertIn("Já existe um cartão", str(context.exception))
    
    def test_get_card_by_id_success(self):
        """Testa obtenção de cartão por ID"""
        # Arrange
        cartao_mock = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_domain.get_card_by_id.return_value = cartao_mock
        
        # Act
        resultado = self.card_service.get_card_by_id("test-id")
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.id, "test-id")
        self.mock_card_domain.get_card_by_id.assert_called_once_with("test-id")
    
    def test_list_cards_active_only(self):
        """Testa listagem apenas de cartões ativos"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=5000, dia_vencimento=10, dia_fechamento=5, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=3000, dia_vencimento=15, dia_fechamento=10, ativo=True)
        ]
        
        self.mock_card_domain.list_cards.return_value = cartoes_mock
        
        # Act
        resultado = self.card_service.list_cards(active_only=True)
        
        # Assert
        self.assertEqual(len(resultado), 2)
        self.mock_card_domain.list_cards.assert_called_once_with(True)
    
    def test_list_cards_shared_only(self):
        """Testa listagem apenas de cartões compartilhados"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=5000, dia_vencimento=10, dia_fechamento=5,
                         compartilhado_com_alzi=True, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=3000, dia_vencimento=15, dia_fechamento=10,
                         compartilhado_com_alzi=False, ativo=True)
        ]
        
        self.mock_card_domain.list_cards.return_value = cartoes_mock
        
        # Act
        resultado = self.card_service.list_cards(shared_with_alzi_only=True)
        
        # Assert
        self.assertEqual(len(resultado), 1)
        self.assertTrue(resultado[0].compartilhado_com_alzi)
    
    def test_update_available_limit_decrease(self):
        """Testa diminuição do limite disponível"""
        # Arrange
        cartao_existente = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_domain.get_card_by_id.return_value = cartao_existente
        self.mock_card_domain.update_card.return_value = True
        
        # Act
        resultado = self.card_service.update_available_limit("test-id", 1000.0, 'decrease')
        
        # Assert
        self.assertTrue(resultado)
        # Verifica se o limite foi atualizado corretamente (5000 - 1000 = 4000)
        call_args = self.mock_card_domain.update_card.call_args
        self.assertEqual(call_args[1]['limite_disponivel'], 4000.0)
    
    def test_update_available_limit_increase(self):
        """Testa aumento do limite disponível"""
        # Arrange
        cartao_existente = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=3000.0,  # Já usado 2000
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_domain.get_card_by_id.return_value = cartao_existente
        self.mock_card_domain.update_card.return_value = True
        
        # Act
        resultado = self.card_service.update_available_limit("test-id", 1000.0, 'increase')
        
        # Assert
        self.assertTrue(resultado)
        # Verifica se o limite foi atualizado corretamente (3000 + 1000 = 4000)
        call_args = self.mock_card_domain.update_card.call_args
        self.assertEqual(call_args[1]['limite_disponivel'], 4000.0)
    
    def test_update_available_limit_increase_capped(self):
        """Testa aumento do limite disponível com cap no limite total"""
        # Arrange
        cartao_existente = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=4500.0,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_domain.get_card_by_id.return_value = cartao_existente
        self.mock_card_domain.update_card.return_value = True
        
        # Act
        resultado = self.card_service.update_available_limit("test-id", 1000.0, 'increase')
        
        # Assert
        self.assertTrue(resultado)
        # Verifica se o limite foi limitado ao máximo (5000)
        call_args = self.mock_card_domain.update_card.call_args
        self.assertEqual(call_args[1]['limite_disponivel'], 5000.0)
    
    def test_update_available_limit_insufficient(self):
        """Testa tentativa de usar mais limite que o disponível"""
        # Arrange
        cartao_existente = CartaoCredito(
            id="test-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=500.0,  # Pouco limite disponível
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_domain.get_card_by_id.return_value = cartao_existente
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.card_service.update_available_limit("test-id", 1000.0, 'decrease')
        
        self.assertIn("Limite insuficiente", str(context.exception))
    
    def test_get_total_limit(self):
        """Testa cálculo dos limites totais"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=4000, dia_vencimento=10, dia_fechamento=5, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=2500, dia_vencimento=15, dia_fechamento=10, ativo=True)
        ]
        
        self.mock_card_domain.list_cards.return_value = cartoes_mock
        
        # Act
        resultado = self.card_service.get_total_limit()
        
        # Assert
        self.assertEqual(resultado['total_limit'], 8000.0)  # 5000 + 3000
        self.assertEqual(resultado['available_limit'], 6500.0)  # 4000 + 2500
        self.assertEqual(resultado['used_limit'], 1500.0)  # (5000-4000) + (3000-2500)
    
    def test_get_shared_cards_summary(self):
        """Testa resumo de cartões compartilhados"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=4000, dia_vencimento=10, dia_fechamento=5,
                         compartilhado_com_alzi=True, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=2500, dia_vencimento=15, dia_fechamento=10,
                         compartilhado_com_alzi=True, ativo=True)
        ]
        
        self.mock_card_domain.list_cards.return_value = cartoes_mock
        
        # Act
        resumo = self.card_service.get_shared_cards_summary()
        
        # Assert
        self.assertEqual(resumo['total_cards'], 2)
        self.assertEqual(resumo['total_limit'], 8000.0)
        self.assertEqual(resumo['available_limit'], 6500.0)
        self.assertEqual(resumo['used_limit'], 1500.0)
        self.assertIn('cards_by_brand', resumo)
        self.assertIn('cards', resumo)
    
    def test_get_cards_by_due_date(self):
        """Testa agrupamento de cartões por dia de vencimento"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=4000, dia_vencimento=10, dia_fechamento=5, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=2500, dia_vencimento=10, dia_fechamento=15, ativo=True),
            CartaoCredito(id="3", nome="Cartão 3", banco="Banco", bandeira=BandeiraCartao.ELO,
                         limite=2000, limite_disponivel=2000, dia_vencimento=20, dia_fechamento=15, ativo=True)
        ]
        
        self.mock_card_domain.list_cards.return_value = cartoes_mock
        
        # Act
        resultado = self.card_service.get_cards_by_due_date()
        
        # Assert
        self.assertIn(10, resultado)
        self.assertIn(20, resultado)
        self.assertEqual(len(resultado[10]), 2)  # Dois cartões vencem no dia 10
        self.assertEqual(len(resultado[20]), 1)  # Um cartão vence no dia 20
    
    def test_validate_billing_dates_valid(self):
        """Testa validação de datas válidas"""
        # Act & Assert
        self.assertTrue(self.card_service.validate_billing_dates(10, 5))
        self.assertTrue(self.card_service.validate_billing_dates(15, 20))
    
    def test_validate_billing_dates_invalid(self):
        """Testa validação de datas inválidas"""
        # Act & Assert
        self.assertFalse(self.card_service.validate_billing_dates(32, 5))  # Dia inválido
        self.assertFalse(self.card_service.validate_billing_dates(10, 10))  # Dias iguais
        self.assertFalse(self.card_service.validate_billing_dates(0, 5))   # Dia zero


if __name__ == '__main__':
    unittest.main()