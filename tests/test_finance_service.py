"""
Testes unitários para FinanceService

Testa o service principal que orquestra todos os outros services.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.services.finance_service import FinanceService
from utils.finance_models import (
    ContaCorrente, CartaoCredito, Transacao, ResumoFinanceiro,
    TipoTransacao, TipoConta, BandeiraCartao
)


class TestFinanceService(unittest.TestCase):
    """Testes para FinanceService"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Mock do DatabaseManager
        self.mock_db_manager = Mock()
        
        # Mocks dos services
        self.mock_account_service = Mock()
        self.mock_card_service = Mock()
        self.mock_transaction_service = Mock()
        self.mock_period_service = Mock()
        self.mock_alzi_service = Mock()
        
        # Patches para os services
        with patch('modules.finances.services.finance_service.AccountService', return_value=self.mock_account_service), \
             patch('modules.finances.services.finance_service.CardService', return_value=self.mock_card_service), \
             patch('modules.finances.services.finance_service.TransactionService', return_value=self.mock_transaction_service), \
             patch('modules.finances.services.finance_service.PeriodService', return_value=self.mock_period_service), \
             patch('modules.finances.services.finance_service.AlziService', return_value=self.mock_alzi_service), \
             patch('modules.finances.services.finance_service.DatabaseManager', return_value=self.mock_db_manager):
            
            self.finance_service = FinanceService()
    
    def test_criar_conta_success(self):
        """Testa criação bem-sucedida de conta"""
        # Arrange
        conta_mock = ContaCorrente(
            id="conta-id",
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0,
            saldo_atual=1000.0,
            ativa=True
        )
        
        self.mock_account_service.create_account.return_value = conta_mock
        
        # Act
        resultado = self.finance_service.criar_conta(
            nome="Conta Teste",
            banco="Banco Teste",
            agencia="1234",
            conta="56789-0",
            tipo=TipoConta.CORRENTE,
            saldo_inicial=1000.0
        )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nome, "Conta Teste")
        self.mock_account_service.create_account.assert_called_once()
    
    def test_criar_cartao_success(self):
        """Testa criação bem-sucedida de cartão"""
        # Arrange
        cartao_mock = CartaoCredito(
            id="cartao-id",
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            limite_disponivel=5000.0,
            dia_vencimento=10,
            dia_fechamento=5,
            ativo=True
        )
        
        self.mock_card_service.create_card.return_value = cartao_mock
        
        # Act
        resultado = self.finance_service.criar_cartao(
            nome="Cartão Teste",
            banco="Banco Teste",
            bandeira=BandeiraCartao.VISA,
            limite=5000.0,
            dia_vencimento=10,
            dia_fechamento=5
        )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nome, "Cartão Teste")
        self.mock_card_service.create_card.assert_called_once()
    
    def test_criar_transacao_success(self):
        """Testa criação bem-sucedida de transação"""
        # Arrange
        transacao_mock = Transacao(
            id="transacao-id",
            descricao="Compra Teste",
            valor=100.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao="2024-01-01",
            conta_id="conta-id",
            parcelamento=[]
        )
        
        self.mock_transaction_service.create_transaction.return_value = transacao_mock
        
        # Act
        resultado = self.finance_service.criar_transacao(
            descricao="Compra Teste",
            valor=100.0,
            tipo=TipoTransacao.DEBITO,
            data_transacao="2024-01-01",
            conta_id="conta-id"
        )
        
        # Assert
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.descricao, "Compra Teste")
        self.mock_transaction_service.create_transaction.assert_called_once()
    
    def test_listar_contas(self):
        """Testa listagem de contas"""
        # Arrange
        contas_mock = [
            ContaCorrente(id="1", nome="Conta 1", banco="Banco", agencia="1", conta="1", 
                         tipo=TipoConta.CORRENTE, saldo_inicial=1000, saldo_atual=1000, ativa=True),
            ContaCorrente(id="2", nome="Conta 2", banco="Banco", agencia="2", conta="2", 
                         tipo=TipoConta.POUPANCA, saldo_inicial=2000, saldo_atual=2000, ativa=True)
        ]
        
        self.mock_account_service.list_accounts.return_value = contas_mock
        
        # Act
        resultado = self.finance_service.listar_contas()
        
        # Assert
        self.assertEqual(len(resultado), 2)
        self.mock_account_service.list_accounts.assert_called_once_with(active_only=True)
    
    def test_listar_cartoes(self):
        """Testa listagem de cartões"""
        # Arrange
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=4000, dia_vencimento=10, dia_fechamento=5, ativo=True),
            CartaoCredito(id="2", nome="Cartão 2", banco="Banco", bandeira=BandeiraCartao.MASTERCARD,
                         limite=3000, limite_disponivel=2500, dia_vencimento=15, dia_fechamento=10, ativo=True)
        ]
        
        self.mock_card_service.list_cards.return_value = cartoes_mock
        
        # Act
        resultado = self.finance_service.listar_cartoes()
        
        # Assert
        self.assertEqual(len(resultado), 2)
        self.mock_card_service.list_cards.assert_called_once_with(active_only=True)
    
    def test_obter_transacoes_mes(self):
        """Testa obtenção de transações do mês"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Transação 1", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", conta_id="conta-id"),
            Transacao(id="2", descricao="Transação 2", valor=200, tipo=TipoTransacao.CREDITO, 
                     data_transacao="2024-01-20", conta_id="conta-id")
        ]
        
        self.mock_transaction_service.get_transactions_by_month.return_value = transacoes_mock
        
        # Act
        resultado = self.finance_service.obter_transacoes_mes(2024, 1)
        
        # Assert
        self.assertEqual(len(resultado), 2)
        self.mock_transaction_service.get_transactions_by_month.assert_called_once_with(2024, 1, False)
    
    def test_obter_transacoes_mes_compartilhadas(self):
        """Testa obtenção apenas de transações compartilhadas do mês"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Transação Compartilhada", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", conta_id="conta-id", compartilhado_com_alzi=True)
        ]
        
        self.mock_transaction_service.get_transactions_by_month.return_value = transacoes_mock
        
        # Act
        resultado = self.finance_service.obter_transacoes_mes(2024, 1, compartilhadas_apenas=True)
        
        # Assert
        self.assertEqual(len(resultado), 1)
        self.mock_transaction_service.get_transactions_by_month.assert_called_once_with(2024, 1, True)
    
    def test_obter_transacoes_fatura_cartao(self):
        """Testa obtenção de transações de fatura de cartão"""
        # Arrange
        transacoes_mock = [
            Transacao(id="1", descricao="Compra Cartão", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", cartao_id="cartao-id")
        ]
        
        self.mock_period_service.get_billing_period_transactions.return_value = transacoes_mock
        
        # Act
        resultado = self.finance_service.obter_transacoes_fatura_cartao("cartao-id", 2, 2024)
        
        # Assert
        self.assertEqual(len(resultado), 1)
        self.mock_period_service.get_billing_period_transactions.assert_called_once_with("cartao-id", 2, 2024)
    
    def test_obter_resumo_compartilhado_atual(self):
        """Testa obtenção do resumo compartilhado atual"""
        # Arrange
        resumo_mock = {
            'periodo': "03/2024",
            'total_debitos': 1000.0,
            'valor_individual': 500.0
        }
        
        self.mock_alzi_service.get_current_month_summary.return_value = resumo_mock
        
        # Act
        resultado = self.finance_service.obter_resumo_compartilhado_atual()
        
        # Assert
        self.assertEqual(resultado['periodo'], "03/2024")
        self.assertEqual(resultado['total_debitos'], 1000.0)
        self.mock_alzi_service.get_current_month_summary.assert_called_once()
    
    @patch('modules.finances.services.finance_service.datetime')
    def test_obter_resumo_financeiro_success(self, mock_datetime):
        """Testa geração de resumo financeiro completo"""
        # Arrange
        mock_datetime.now.return_value = datetime(2024, 3, 15)
        
        # Mocks das listas
        contas_mock = [
            ContaCorrente(id="1", nome="Conta 1", banco="Banco", agencia="1", conta="1", 
                         tipo=TipoConta.CORRENTE, saldo_inicial=1000, saldo_atual=1500, 
                         compartilhado_com_alzi=True, ativa=True)
        ]
        
        cartoes_mock = [
            CartaoCredito(id="1", nome="Cartão 1", banco="Banco", bandeira=BandeiraCartao.VISA,
                         limite=5000, limite_disponivel=4000, dia_vencimento=10, dia_fechamento=5,
                         compartilhado_com_alzi=True, ativo=True)
        ]
        
        transacoes_mes_mock = [
            Transacao(id="1", descricao="Débito", valor=200, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-03-10", conta_id="1"),
            Transacao(id="2", descricao="Crédito", valor=100, tipo=TipoTransacao.CREDITO, 
                     data_transacao="2024-03-15", conta_id="1")
        ]
        
        transacoes_compartilhadas_mock = [
            Transacao(id="3", descricao="Débito Compartilhado", valor=150, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-03-12", conta_id="1", compartilhado_com_alzi=True)
        ]
        
        # Configurar mocks
        self.mock_account_service.list_accounts.return_value = contas_mock
        self.mock_card_service.list_cards.return_value = cartoes_mock
        self.mock_transaction_service.get_transactions_by_month.side_effect = [
            transacoes_mes_mock,  # Primeira chamada (todas as transações)
            transacoes_compartilhadas_mock  # Segunda chamada (apenas compartilhadas)
        ]
        
        # Act
        resultado = self.finance_service.obter_resumo_financeiro()
        
        # Assert
        self.assertIsInstance(resultado, ResumoFinanceiro)
        self.assertEqual(resultado.total_contas, 1)
        self.assertEqual(resultado.total_cartoes, 1)
        self.assertEqual(resultado.total_transacoes, 2)
        self.assertEqual(resultado.saldo_total_contas, 1500.0)
        self.assertEqual(resultado.limite_total_cartoes, 5000.0)
        self.assertEqual(resultado.limite_disponivel_cartoes, 4000.0)
        self.assertEqual(resultado.valor_total_gastos_mes, 200.0)  # Apenas débitos
        self.assertEqual(resultado.valor_compartilhado_alzi_mes, 150.0)
        self.assertEqual(resultado.contas_compartilhadas, 1)
        self.assertEqual(resultado.cartoes_compartilhados, 1)
        self.assertEqual(resultado.transacoes_compartilhadas_mes, 1)
    
    def test_detectar_formato_csv_bradesco(self):
        """Testa detecção de formato Bradesco"""
        # Arrange
        with patch('builtins.open', mock_open_with_content("Data;Histórico;Valor(US$);Valor(R$);\ndata")):
            # Act
            resultado = self.finance_service.detectar_formato_csv("test.csv")
        
        # Assert
        self.assertEqual(resultado, "bradesco")
    
    def test_detectar_formato_csv_nao_suportado(self):
        """Testa detecção de formato não suportado"""
        # Arrange
        with patch('builtins.open', mock_open_with_content("formato,desconhecido\ndata,data")):
            # Act
            resultado = self.finance_service.detectar_formato_csv("test.csv")
        
        # Assert
        self.assertIsNone(resultado)
    
    def test_excluir_fatura_completa_success(self):
        """Testa exclusão completa de fatura"""
        # Arrange
        transacoes_fatura = [
            Transacao(id="1", descricao="Compra 1", valor=100, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-15", cartao_id="cartao-id"),
            Transacao(id="2", descricao="Compra 2", valor=200, tipo=TipoTransacao.DEBITO, 
                     data_transacao="2024-01-20", cartao_id="cartao-id")
        ]
        
        resultado_exclusao = {
            'sucesso': True,
            'total_requested': 2,
            'deleted': 2,
            'errors': []
        }
        
        # Mock dos métodos chamados
        with patch.object(self.finance_service, 'obter_transacoes_fatura_cartao', return_value=transacoes_fatura), \
             patch.object(self.finance_service, 'excluir_multiplas_transacoes', return_value=resultado_exclusao):
            
            # Act
            resultado = self.finance_service.excluir_fatura_completa("cartao-id", 2, 2024)
        
        # Assert
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(resultado['total_transacoes'], 2)
        self.assertEqual(resultado['excluidas'], 2)
        self.assertEqual(resultado['mes_fatura'], 2)
        self.assertEqual(resultado['ano_fatura'], 2024)
    
    def test_excluir_fatura_completa_sem_transacoes(self):
        """Testa exclusão de fatura sem transações"""
        # Arrange
        with patch.object(self.finance_service, 'obter_transacoes_fatura_cartao', return_value=[]):
            # Act
            resultado = self.finance_service.excluir_fatura_completa("cartao-id", 2, 2024)
        
        # Assert
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(resultado['total_transacoes'], 0)
        self.assertEqual(resultado['excluidas'], 0)
    
    def test_obter_relatorio_completo_alzi(self):
        """Testa obtenção de relatório completo do Alzi"""
        # Arrange
        relatorio_mock = {
            'periodo': "01/2024",
            'resumo_geral': {'total_gasto_compartilhado': 1000.0},
            'insights': ['Insight 1', 'Insight 2']
        }
        
        self.mock_alzi_service.get_comprehensive_shared_report.return_value = relatorio_mock
        
        # Act
        resultado = self.finance_service.obter_relatorio_completo_alzi(2024, 1)
        
        # Assert
        self.assertEqual(resultado['periodo'], "01/2024")
        self.assertIn('resumo_geral', resultado)
        self.assertIn('insights', resultado)
        self.mock_alzi_service.get_comprehensive_shared_report.assert_called_once_with(2024, 1)


def mock_open_with_content(content):
    """Helper para criar mock do open com conteúdo específico"""
    from unittest.mock import mock_open
    return mock_open(read_data=content)


if __name__ == '__main__':
    unittest.main()