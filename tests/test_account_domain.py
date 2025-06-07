"""
Testes unitários para AccountDomain

Testa todas as regras de negócio relacionadas a contas correntes,
poupança e investimento.
"""

import unittest
from datetime import datetime
from decimal import Decimal

# Adicionar caminho para imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.domains import AccountDomain
from utils.finance_models import ContaCorrente, TipoConta, TipoTransacao


class TestAccountDomain(unittest.TestCase):
    """Testes para AccountDomain"""

    def setUp(self):
        """Setup para cada teste"""
        self.valid_account_data = {
            'nome': 'Conta Teste',
            'banco': 'Banco Teste',
            'agencia': '1234',
            'conta': '56789-0',
            'tipo': TipoConta.CORRENTE,
            'saldo_inicial': 1000.0
        }

    def test_validate_account_data_valid(self):
        """Testa validação com dados válidos"""
        result = AccountDomain.validate_account_data(**self.valid_account_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_validate_account_data_invalid_nome(self):
        """Testa validação com nome inválido"""
        data = self.valid_account_data.copy()
        data['nome'] = 'A'  # Muito curto
        
        result = AccountDomain.validate_account_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Nome da conta deve ter pelo menos 2 caracteres', result['errors'])

    def test_validate_account_data_invalid_banco(self):
        """Testa validação com banco inválido"""
        data = self.valid_account_data.copy()
        data['banco'] = ''  # Vazio
        
        result = AccountDomain.validate_account_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Nome do banco deve ter pelo menos 2 caracteres', result['errors'])

    def test_validate_account_data_invalid_agencia(self):
        """Testa validação com agência inválida"""
        data = self.valid_account_data.copy()
        data['agencia'] = '12'  # Muito curto
        
        result = AccountDomain.validate_account_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Agência deve ter pelo menos 3 caracteres', result['errors'])

    def test_validate_account_data_invalid_conta(self):
        """Testa validação com conta inválida"""
        data = self.valid_account_data.copy()
        data['conta'] = '123'  # Muito curto
        
        result = AccountDomain.validate_account_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Número da conta deve ter pelo menos 4 caracteres', result['errors'])

    def test_validate_account_data_negative_balance_poupanca(self):
        """Testa validação com saldo negativo em poupança"""
        data = self.valid_account_data.copy()
        data['tipo'] = TipoConta.POUPANCA
        data['saldo_inicial'] = -100.0
        
        result = AccountDomain.validate_account_data(**data)
        
        self.assertFalse(result['valid'])
        self.assertIn('Saldo inicial não pode ser negativo para poupança e investimento', result['errors'])

    def test_calculate_new_balance_debito(self):
        """Testa cálculo de novo saldo para débito"""
        new_balance = AccountDomain.calculate_new_balance(1000.0, 150.0, TipoTransacao.DEBITO)
        
        self.assertEqual(new_balance, 850.0)

    def test_calculate_new_balance_credito(self):
        """Testa cálculo de novo saldo para crédito"""
        new_balance = AccountDomain.calculate_new_balance(1000.0, 150.0, TipoTransacao.CREDITO)
        
        self.assertEqual(new_balance, 1150.0)

    def test_calculate_new_balance_precision(self):
        """Testa precisão do cálculo de saldo"""
        new_balance = AccountDomain.calculate_new_balance(100.0, 33.33, TipoTransacao.DEBITO)
        
        self.assertEqual(new_balance, 66.67)

    def test_can_account_be_deleted_with_transactions(self):
        """Testa se conta com transações pode ser excluída"""
        account = ContaCorrente(
            id='test',
            nome='Teste',
            banco='Banco',
            agencia='1234',
            conta='5678',
            tipo=TipoConta.CORRENTE,
            saldo_inicial=0.0,
            saldo_atual=0.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        result = AccountDomain.can_account_be_deleted(account, has_transactions=True)
        
        self.assertFalse(result['can_delete'])
        self.assertIn('transações', result['reason'])

    def test_can_account_be_deleted_with_balance(self):
        """Testa se conta com saldo pode ser excluída"""
        account = ContaCorrente(
            id='test',
            nome='Teste',
            banco='Banco',
            agencia='1234',
            conta='5678',
            tipo=TipoConta.CORRENTE,
            saldo_inicial=100.0,
            saldo_atual=100.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        result = AccountDomain.can_account_be_deleted(account, has_transactions=False)
        
        self.assertFalse(result['can_delete'])
        self.assertIn('saldo zero', result['reason'])

    def test_can_account_be_deleted_valid(self):
        """Testa se conta válida pode ser excluída"""
        account = ContaCorrente(
            id='test',
            nome='Teste',
            banco='Banco',
            agencia='1234',
            conta='5678',
            tipo=TipoConta.CORRENTE,
            saldo_inicial=0.0,
            saldo_atual=0.0,
            compartilhado_com_alzi=False,
            ativa=True
        )
        
        result = AccountDomain.can_account_be_deleted(account, has_transactions=False)
        
        self.assertTrue(result['can_delete'])
        self.assertEqual(result['reason'], '')

    def test_calculate_accounts_summary(self):
        """Testa cálculo de resumo de contas"""
        accounts = [
            ContaCorrente(
                id='1', nome='Conta 1', banco='Banco', agencia='1234', conta='5678',
                tipo=TipoConta.CORRENTE, saldo_inicial=1000.0, saldo_atual=1000.0,
                compartilhado_com_alzi=True, ativa=True
            ),
            ContaCorrente(
                id='2', nome='Conta 2', banco='Banco', agencia='1234', conta='5679',
                tipo=TipoConta.POUPANCA, saldo_inicial=500.0, saldo_atual=500.0,
                compartilhado_com_alzi=False, ativa=True
            ),
            ContaCorrente(
                id='3', nome='Conta 3', banco='Banco', agencia='1234', conta='5680',
                tipo=TipoConta.CORRENTE, saldo_inicial=200.0, saldo_atual=200.0,
                compartilhado_com_alzi=False, ativa=False  # Inativa
            )
        ]
        
        summary = AccountDomain.calculate_accounts_summary(accounts)
        
        self.assertEqual(summary['total_accounts'], 2)  # Apenas ativas
        self.assertEqual(summary['total_balance'], 1500.0)
        self.assertEqual(summary['shared_accounts_count'], 1)
        self.assertEqual(summary['shared_accounts_balance'], 1000.0)
        self.assertEqual(summary['balance_by_type']['corrente'], 1000.0)
        self.assertEqual(summary['balance_by_type']['poupanca'], 500.0)
        self.assertEqual(summary['inactive_accounts'], 1)

    def test_generate_account_id(self):
        """Testa geração de ID único"""
        id1 = AccountDomain.generate_account_id()
        id2 = AccountDomain.generate_account_id()
        
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        self.assertNotEqual(id1, id2)
        self.assertTrue(len(id1) > 30)  # UUID tem mais de 30 caracteres

    def test_prepare_account_creation_data(self):
        """Testa preparação de dados para criação"""
        data = AccountDomain.prepare_account_creation_data(
            nome='  Conta Teste  ',  # Com espaços
            banco='Banco Teste',
            agencia='1234',
            conta='56789-0',
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            compartilhado_com_alzi=True
        )
        
        self.assertEqual(data['nome'], 'Conta Teste')  # Espaços removidos
        self.assertEqual(data['saldo_inicial'], 1000.0)
        self.assertEqual(data['saldo_atual'], 1000.0)  # Regra: igual ao inicial
        self.assertTrue(data['ativa'])  # Regra: sempre ativa
        self.assertTrue(data['compartilhado_com_alzi'])
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_prepare_account_update_data(self):
        """Testa preparação de dados para atualização"""
        account = ContaCorrente(
            id='test', nome='Teste', banco='Banco', agencia='1234', conta='5678',
            tipo=TipoConta.CORRENTE, saldo_inicial=1000.0, saldo_atual=1000.0,
            compartilhado_com_alzi=False, ativa=True
        )
        
        update_data = AccountDomain.prepare_account_update_data(
            account,
            nome='Novo Nome',
            saldo_atual=1500.0,
            invalid_field='ignored'  # Campo inválido deve ser ignorado
        )
        
        self.assertEqual(update_data['nome'], 'Novo Nome')
        self.assertEqual(update_data['saldo_atual'], 1500.0)
        self.assertNotIn('invalid_field', update_data)
        self.assertIn('updated_at', update_data)

    def test_filter_accounts_by_criteria(self):
        """Testa filtros de contas"""
        accounts = [
            ContaCorrente(
                id='1', nome='Conta 1', banco='Banco', agencia='1234', conta='5678',
                tipo=TipoConta.CORRENTE, saldo_inicial=1000.0, saldo_atual=1000.0,
                compartilhado_com_alzi=True, ativa=True
            ),
            ContaCorrente(
                id='2', nome='Conta 2', banco='Banco', agencia='1234', conta='5679',
                tipo=TipoConta.POUPANCA, saldo_inicial=500.0, saldo_atual=500.0,
                compartilhado_com_alzi=False, ativa=True
            ),
            ContaCorrente(
                id='3', nome='Conta 3', banco='Banco', agencia='1234', conta='5680',
                tipo=TipoConta.CORRENTE, saldo_inicial=200.0, saldo_atual=200.0,
                compartilhado_com_alzi=True, ativa=False
            )
        ]
        
        # Filtrar apenas ativas
        ativas = AccountDomain.filter_accounts_by_criteria(accounts, ativas_apenas=True)
        self.assertEqual(len(ativas), 2)
        
        # Filtrar apenas compartilhadas
        compartilhadas = AccountDomain.filter_accounts_by_criteria(
            accounts, ativas_apenas=False, compartilhadas_apenas=True
        )
        self.assertEqual(len(compartilhadas), 2)
        
        # Filtrar por tipo
        correntes = AccountDomain.filter_accounts_by_criteria(
            accounts, ativas_apenas=False, tipo=TipoConta.CORRENTE
        )
        self.assertEqual(len(correntes), 2)

    def test_is_account_balance_valid_for_transaction_credito(self):
        """Testa validação de saldo para crédito"""
        account = ContaCorrente(
            id='test', nome='Teste', banco='Banco', agencia='1234', conta='5678',
            tipo=TipoConta.CORRENTE, saldo_inicial=100.0, saldo_atual=100.0,
            compartilhado_com_alzi=False, ativa=True
        )
        
        result = AccountDomain.is_account_balance_valid_for_transaction(
            account, 1000.0, TipoTransacao.CREDITO
        )
        
        self.assertTrue(result['valid'])  # Crédito sempre válido

    def test_is_account_balance_valid_for_transaction_debito_corrente(self):
        """Testa validação de saldo para débito em conta corrente"""
        account = ContaCorrente(
            id='test', nome='Teste', banco='Banco', agencia='1234', conta='5678',
            tipo=TipoConta.CORRENTE, saldo_inicial=100.0, saldo_atual=100.0,
            compartilhado_com_alzi=False, ativa=True
        )
        
        # Conta corrente pode ficar negativa
        result = AccountDomain.is_account_balance_valid_for_transaction(
            account, 1000.0, TipoTransacao.DEBITO
        )
        
        self.assertTrue(result['valid'])

    def test_is_account_balance_valid_for_transaction_debito_poupanca(self):
        """Testa validação de saldo para débito em poupança"""
        account = ContaCorrente(
            id='test', nome='Teste', banco='Banco', agencia='1234', conta='5678',
            tipo=TipoConta.POUPANCA, saldo_inicial=100.0, saldo_atual=100.0,
            compartilhado_com_alzi=False, ativa=True
        )
        
        # Poupança não pode ficar negativa
        result = AccountDomain.is_account_balance_valid_for_transaction(
            account, 1000.0, TipoTransacao.DEBITO
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('Saldo insuficiente', result['message'])


if __name__ == '__main__':
    unittest.main()