"""
Configurações para testes dos services

Centralizamos aqui configurações comuns para todos os testes dos services.
"""

import os
import sys
from unittest.mock import Mock

# Adicionar caminho do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)


class TestConfig:
    """Configurações centralizadas para testes"""
    
    # Configurações de ambiente de teste
    TEST_DATABASE_NAME = "lifeos_test"
    TEST_MONGODB_HOST = "localhost"
    TEST_MONGODB_PORT = 27017
    
    # IDs de teste padronizados
    TEST_ACCOUNT_ID = "test-account-id-12345"
    TEST_CARD_ID = "test-card-id-12345"
    TEST_TRANSACTION_ID = "test-transaction-id-12345"
    
    # Valores de teste padronizados
    TEST_INITIAL_BALANCE = 1000.0
    TEST_CARD_LIMIT = 5000.0
    TEST_TRANSACTION_VALUE = 100.0
    
    # Datas de teste
    TEST_DATE = "2024-01-15"
    TEST_YEAR = 2024
    TEST_MONTH = 1
    
    @staticmethod
    def create_mock_database_manager():
        """Cria um mock padronizado do DatabaseManager"""
        mock_db = Mock()
        mock_db.is_connected.return_value = True
        mock_db.db_name = TestConfig.TEST_DATABASE_NAME
        mock_db.collection.return_value = Mock()
        return mock_db
    
    @staticmethod
    def get_test_account_data():
        """Retorna dados de teste para conta"""
        return {
            'id': TestConfig.TEST_ACCOUNT_ID,
            'nome': 'Conta Teste',
            'banco': 'Banco Teste',
            'agencia': '1234',
            'conta': '56789-0',
            'tipo': 'corrente',
            'saldo_inicial': TestConfig.TEST_INITIAL_BALANCE,
            'saldo_atual': TestConfig.TEST_INITIAL_BALANCE,
            'compartilhado_com_alzi': False,
            'ativa': True,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
    
    @staticmethod
    def get_test_card_data():
        """Retorna dados de teste para cartão"""
        return {
            'id': TestConfig.TEST_CARD_ID,
            'nome': 'Cartão Teste',
            'banco': 'Banco Teste',
            'bandeira': 'visa',
            'limite': TestConfig.TEST_CARD_LIMIT,
            'limite_disponivel': TestConfig.TEST_CARD_LIMIT,
            'dia_vencimento': 10,
            'dia_fechamento': 5,
            'compartilhado_com_alzi': False,
            'ativo': True,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
    
    @staticmethod
    def get_test_transaction_data():
        """Retorna dados de teste para transação"""
        return {
            'id': TestConfig.TEST_TRANSACTION_ID,
            'descricao': 'Transação Teste',
            'valor': TestConfig.TEST_TRANSACTION_VALUE,
            'tipo': 'debito',
            'data_transacao': TestConfig.TEST_DATE,
            'categoria': 'Teste',
            'conta_id': TestConfig.TEST_ACCOUNT_ID,
            'cartao_id': None,
            'parcelamento': [],
            'observacoes': None,
            'status': 'processada',
            'compartilhado_com_alzi': False,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }


class TestHelpers:
    """Helpers úteis para testes"""
    
    @staticmethod
    def assert_mock_called_with_partial(mock_call, expected_params):
        """Verifica se um mock foi chamado com parâmetros específicos"""
        call_args = mock_call.call_args
        if call_args is None:
            return False
        
        for key, value in expected_params.items():
            if key not in call_args[1] or call_args[1][key] != value:
                return False
        
        return True
    
    @staticmethod
    def create_mock_service_with_methods(methods_dict):
        """Cria um mock de service com métodos específicos"""
        mock_service = Mock()
        for method_name, return_value in methods_dict.items():
            getattr(mock_service, method_name).return_value = return_value
        return mock_service
    
    @staticmethod
    def validate_service_call_order(mock_service, expected_calls):
        """Valida a ordem de chamadas em um service"""
        actual_calls = [call[0] for call in mock_service.method_calls]
        return actual_calls == expected_calls


class TestConstants:
    """Constantes utilizadas nos testes"""
    
    # Mensagens de erro esperadas
    ERROR_MESSAGES = {
        'INVALID_NAME': 'Nome',
        'INVALID_BANK': 'banco',
        'INVALID_VALUE': 'Valor',
        'INVALID_DATE': 'data',
        'NOT_FOUND': 'não encontrada',
        'DUPLICATE': 'Já existe',
        'INSUFFICIENT_LIMIT': 'Limite insuficiente'
    }
    
    # Códigos de status HTTP simulados
    HTTP_STATUS = {
        'OK': 200,
        'CREATED': 201,
        'BAD_REQUEST': 400,
        'NOT_FOUND': 404,
        'INTERNAL_ERROR': 500
    }
    
    # Tipos de transação
    TRANSACTION_TYPES = {
        'DEBIT': 'debito',
        'CREDIT': 'credito'
    }
    
    # Tipos de conta
    ACCOUNT_TYPES = {
        'CHECKING': 'corrente',
        'SAVINGS': 'poupanca',
        'INVESTMENT': 'investimento'
    }
    
    # Bandeiras de cartão
    CARD_BRANDS = {
        'VISA': 'visa',
        'MASTERCARD': 'mastercard',
        'ELO': 'elo',
        'AMERICAN_EXPRESS': 'american_express'
    }


class MockFactories:
    """Factories para criar mocks padronizados"""
    
    @staticmethod
    def create_account_mock(**overrides):
        """Cria mock de conta com valores padrão"""
        from utils.finance_models import ContaCorrente, TipoConta
        
        defaults = TestConfig.get_test_account_data()
        defaults.update(overrides)
        
        return ContaCorrente(
            id=defaults['id'],
            nome=defaults['nome'],
            banco=defaults['banco'],
            agencia=defaults['agencia'],
            conta=defaults['conta'],
            tipo=TipoConta.CORRENTE,
            saldo_inicial=defaults['saldo_inicial'],
            saldo_atual=defaults['saldo_atual'],
            compartilhado_com_alzi=defaults['compartilhado_com_alzi'],
            ativa=defaults['ativa'],
            created_at=defaults['created_at'],
            updated_at=defaults['updated_at']
        )
    
    @staticmethod
    def create_card_mock(**overrides):
        """Cria mock de cartão com valores padrão"""
        from utils.finance_models import CartaoCredito, BandeiraCartao
        
        defaults = TestConfig.get_test_card_data()
        defaults.update(overrides)
        
        return CartaoCredito(
            id=defaults['id'],
            nome=defaults['nome'],
            banco=defaults['banco'],
            bandeira=BandeiraCartao.VISA,
            limite=defaults['limite'],
            limite_disponivel=defaults['limite_disponivel'],
            dia_vencimento=defaults['dia_vencimento'],
            dia_fechamento=defaults['dia_fechamento'],
            compartilhado_com_alzi=defaults['compartilhado_com_alzi'],
            ativo=defaults['ativo'],
            created_at=defaults['created_at'],
            updated_at=defaults['updated_at']
        )
    
    @staticmethod
    def create_transaction_mock(**overrides):
        """Cria mock de transação com valores padrão"""
        from utils.finance_models import Transacao, TipoTransacao, StatusTransacao
        
        defaults = TestConfig.get_test_transaction_data()
        defaults.update(overrides)
        
        return Transacao(
            id=defaults['id'],
            descricao=defaults['descricao'],
            valor=defaults['valor'],
            tipo=TipoTransacao.DEBITO,
            data_transacao=defaults['data_transacao'],
            categoria=defaults['categoria'],
            conta_id=defaults['conta_id'],
            cartao_id=defaults['cartao_id'],
            parcelamento=defaults['parcelamento'],
            observacoes=defaults['observacoes'],
            status=StatusTransacao.PROCESSADA,
            compartilhado_com_alzi=defaults['compartilhado_com_alzi'],
            created_at=defaults['created_at'],
            updated_at=defaults['updated_at']
        )