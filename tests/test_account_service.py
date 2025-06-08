"""
Testes unitários para AccountService

Testa toda a lógica de negócios relacionada ao gerenciamento de contas correntes.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.services.account_service import AccountService
from utils.finance_models import ContaCorrente, TipoConta, TipoTransacao


class TestAccountService(unittest.TestCase):
    """Testes para AccountService"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Mock do DatabaseManager
        self.mock_db_manager = Mock()
        
        # Mock do AccountDomain
        with patch('modules.finances.services.account_service.AccountDomain') as mock_domain_class:
            self.mock_account_domain = Mock()
            mock_domain_class.return_value = self.mock_account_domain
            
            # Criar service com mocks
            self.account_service = AccountService(self.mock_db_manager)
    
    def test_create_account_success(self):
        """Testa criação bem-sucedida de conta"""
        # Arrange
        conta_mock = ContaCorrente(
            id="test-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        self.mock_account_domain.create_account.return_value = conta_mock
        self.mock_account_domain.list_accounts.return_value = []  # Nenhuma conta existente
        
        # Act
        resultado = self.account_service.create_account(
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            compartilhado_com_alzi=False
        )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nome, "Conta Teste")
        self.assertEqual(resultado.banco, "Banco Teste")
        self.mock_account_domain.create_account.assert_called_once()
    
    def test_create_account_invalid_name(self):
        """Testa criação de conta com nome inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_service.create_account(
                nome="",  # Nome vazio
                banco="Banco Teste",
                agencia="1234",
                conta="56789-0",
                tipo=TipoConta.CORRENTE,
                saldo_inicial=1000.0
            )
        
        self.assertIn("Nome da conta é obrigatório", str(context.exception))
    
    def test_create_account_invalid_bank(self):
        """Testa criação de conta com banco inválido"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_service.create_account(
                nome="Conta Teste",
                banco="",  # Banco vazio
                agencia="1234",
                conta="56789-0",
                tipo=TipoConta.CORRENTE,
                saldo_inicial=1000.0
            )
        
        self.assertIn("Nome do banco é obrigatório", str(context.exception))
    
    def test_create_account_negative_balance(self):
        """Testa criação de conta com saldo negativo"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_service.create_account(
                nome="Conta Teste",
                banco="Banco Teste",
                agencia="1234",
                conta="56789-0",
                tipo=TipoConta.CORRENTE,
                saldo_inicial=-100.0  # Saldo negativo
            )
        
        self.assertIn("Saldo inicial não pode ser negativo", str(context.exception))
    
    def test_create_account_duplicate(self):
        """Testa criação de conta duplicada"""
        # Arrange
        conta_existente = ContaCorrente(
            id="existing-id",
            nome="Conta Existente",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.list_accounts.return_value = [conta_existente]
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_service.create_account(
                nome="Nova Conta",
                banco="Banco Teste",  # Mesmo banco
                agencia="1234",       # Mesma agência
                conta="56789-0",      # Mesma conta
                tipo=TipoConta.CORRENTE,
                saldo_inicial=1000.0
            )
        
        self.assertIn("Já existe uma conta", str(context.exception))
    
    def test_get_account_by_id_success(self):
        """Testa obtenção de conta por ID"""
        # Arrange
        conta_mock = ContaCorrente(
            id="test-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.get_account_by_id.return_value = conta_mock
        
        # Act
        resultado = self.account_service.get_account_by_id("test-id")
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.id, "test-id")
        self.mock_account_domain.get_account_by_id.assert_called_once_with("test-id")
    
    def test_get_account_by_id_not_found(self):
        """Testa obtenção de conta inexistente"""
        # Arrange
        self.mock_account_domain.get_account_by_id.return_value = None
        
        # Act
        resultado = self.account_service.get_account_by_id("invalid-id")
        
        # Assert
        self.assertIsNone(resultado)
    
    def test_get_account_by_id_empty_id(self):
        """Testa obtenção de conta com ID vazio"""
        # Act
        resultado = self.account_service.get_account_by_id("")
        
        # Assert
        self.assertIsNone(resultado)
    
    def test_list_accounts_active_only(self):
        """Testa listagem apenas de contas ativas"""
        # Arrange
        contas_mock = [
            ContaCorrente(id="1", nome="Conta 1", banco="Banco", agencia="1", conta="1", 
                         tipo=TipoConta.CORRENTE, saldo_inicial=1000, saldo_atual=1000, ativa=True),
            ContaCorrente(id="2", nome="Conta 2", banco="Banco", agencia="2", conta="2", 
                         tipo=TipoConta.POUPANCA, saldo_inicial=2000, saldo_atual=2000, ativa=True)
        ]
        
        self.mock_account_domain.list_accounts.return_value = contas_mock
        
        # Act
        resultado = self.account_service.list_accounts(active_only=True)
        
        # Assert
        self.assertEqual(len(resultado), 2)
        self.mock_account_domain.list_accounts.assert_called_once_with(True)
    
    def test_list_accounts_shared_only(self):
        """Testa listagem apenas de contas compartilhadas"""
        # Arrange
        contas_mock = [
            ContaCorrente(id="1", nome="Conta 1", banco="Banco", agencia="1", conta="1", 
                         tipo=TipoConta.CORRENTE, saldo_inicial=1000, saldo_atual=1000, 
                         compartilhado_com_alzi=True, ativa=True),
            ContaCorrente(id="2", nome="Conta 2", banco="Banco", agencia="2", conta="2", 
                         tipo=TipoConta.POUPANCA, saldo_inicial=2000, saldo_atual=2000, 
                         compartilhado_com_alzi=False, ativa=True)
        ]
        
        self.mock_account_domain.list_accounts.return_value = contas_mock
        
        # Act
        resultado = self.account_service.list_accounts(shared_with_alzi_only=True)
        
        # Assert
        self.assertEqual(len(resultado), 1)
        self.assertTrue(resultado[0].compartilhado_com_alzi)
    
    def test_update_account_success(self):
        """Testa atualização bem-sucedida de conta"""
        # Arrange
        conta_existente = ContaCorrente(
            id="test-id",
            nome="Conta Original",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.get_account_by_id.return_value = conta_existente
        self.mock_account_domain.update_account.return_value = True
        self.mock_account_domain.list_accounts.return_value = [conta_existente]
        
        # Act
        resultado = self.account_service.update_account("test-id", nome="Conta Atualizada")
        
        # Assert
        self.assertTrue(resultado)
        self.mock_account_domain.update_account.assert_called_once()
    
    def test_update_account_not_found(self):
        """Testa atualização de conta inexistente"""
        # Arrange
        self.mock_account_domain.get_account_by_id.return_value = None
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_service.update_account("invalid-id", nome="Novo Nome")
        
        self.assertIn("Conta não encontrada", str(context.exception))
    
    def test_update_account_empty_name(self):
        """Testa atualização com nome vazio"""
        # Arrange
        conta_existente = ContaCorrente(
            id="test-id",
            nome="Conta Original",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.get_account_by_id.return_value = conta_existente
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_service.update_account("test-id", nome="")
        
        self.assertIn("Nome da conta não pode ser vazio", str(context.exception))
    
    def test_deactivate_account_success(self):
        """Testa desativação bem-sucedida de conta"""
        # Arrange
        conta_existente = ContaCorrente(
            id="test-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.get_account_by_id.return_value = conta_existente
        self.mock_account_domain.update_account.return_value = True
        
        # Act
        resultado = self.account_service.deactivate_account("test-id")
        
        # Assert
        self.assertTrue(resultado)
        self.mock_account_domain.update_account.assert_called_once_with("test-id", ativa=False)
    
    def test_update_balance_debit(self):
        """Testa atualização de saldo com débito"""
        # Arrange
        conta_existente = ContaCorrente(
            id="test-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.get_account_by_id.return_value = conta_existente
        self.mock_account_domain.update_account.return_value = True
        
        # Act
        resultado = self.account_service.update_balance("test-id", 500.0, TipoTransacao.DEBITO)
        
        # Assert
        self.assertTrue(resultado)
        # Verifica se o saldo foi atualizado corretamente (1000 - 500 = 500)
        call_args = self.mock_account_domain.update_account.call_args
        self.assertEqual(call_args[1]['saldo_atual'], 500.0)
    
    def test_update_balance_credit(self):
        """Testa atualização de saldo com crédito"""
        # Arrange
        conta_existente = ContaCorrente(
            id="test-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        self.mock_account_domain.get_account_by_id.return_value = conta_existente
        self.mock_account_domain.update_account.return_value = True
        
        # Act
        resultado = self.account_service.update_balance("test-id", 300.0, TipoTransacao.CREDITO)
        
        # Assert
        self.assertTrue(resultado)
        # Verifica se o saldo foi atualizado corretamente (1000 + 300 = 1300)
        call_args = self.mock_account_domain.update_account.call_args
        self.assertEqual(call_args[1]['saldo_atual'], 1300.0)
    
    def test_get_total_balance(self):
        """Testa cálculo do saldo total"""
        # Arrange
        contas_mock = [
            ContaCorrente(id="1", nome="Conta 1", banco="Banco", agencia="1", conta="1", 
                         tipo=TipoConta.CORRENTE, saldo_inicial=1000, saldo_atual=1500, ativa=True),
            ContaCorrente(id="2", nome="Conta 2", banco="Banco", agencia="2", conta="2", 
                         tipo=TipoConta.POUPANCA, saldo_inicial=2000, saldo_atual=2500, ativa=True)
        ]
        
        self.mock_account_domain.list_accounts.return_value = contas_mock
        
        # Act
        total = self.account_service.get_total_balance()
        
        # Assert
        self.assertEqual(total, 4000.0)  # 1500 + 2500
    
    def test_get_shared_accounts_summary(self):
        """Testa resumo de contas compartilhadas"""
        # Arrange
        contas_mock = [
            ContaCorrente(id="1", nome="Conta 1", banco="Banco", agencia="1", conta="1", 
                         tipo=TipoConta.CORRENTE, saldo_inicial=1000, saldo_atual=1500, 
                         compartilhado_com_alzi=True, ativa=True),
            ContaCorrente(id="2", nome="Conta 2", banco="Banco", agencia="2", conta="2", 
                         tipo=TipoConta.POUPANCA, saldo_inicial=2000, saldo_atual=2500, 
                         compartilhado_com_alzi=True, ativa=True)
        ]
        
        self.mock_account_domain.list_accounts.return_value = contas_mock
        
        # Act
        resumo = self.account_service.get_shared_accounts_summary()
        
        # Assert
        self.assertEqual(resumo['total_accounts'], 2)
        self.assertEqual(resumo['total_balance'], 4000.0)
        self.assertIn('accounts_by_type', resumo)
        self.assertIn('accounts', resumo)


if __name__ == '__main__':
    unittest.main()