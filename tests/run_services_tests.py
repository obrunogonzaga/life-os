"""
Script para executar todos os testes unitários dos services

Este script executa todos os testes dos 6 services criados na Fase 2
da refatoração do módulo finances.
"""

import unittest
import sys
import os
from io import StringIO
import time

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar todos os testes dos services
from test_account_service import TestAccountService
from test_card_service import TestCardService
from test_transaction_service import TestTransactionService
from test_period_service import TestPeriodService
from test_alzi_service import TestAlziService
from test_finance_service import TestFinanceService


class ServiceTestRunner:
    """Runner customizado para testes dos services"""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_skipped = 0
    
    def create_services_test_suite(self):
        """Cria suite com todos os testes dos services"""
        suite = unittest.TestSuite()
        
        # Ordem de execução dos testes (do mais básico ao mais complexo)
        test_classes = [
            ('AccountService', TestAccountService),
            ('CardService', TestCardService),
            ('TransactionService', TestTransactionService),
            ('PeriodService', TestPeriodService),
            ('AlziService', TestAlziService),
            ('FinanceService', TestFinanceService)
        ]
        
        for service_name, test_class in test_classes:
            suite.addTest(unittest.makeSuite(test_class))
        
        return suite, test_classes
    
    def run_all_services_tests(self):
        """Executa todos os testes dos services com relatório detalhado"""
        print("🧪 Executando testes unitários dos SERVICES...")
        print("=" * 80)
        print("📋 FASE 2 - SERVICES LAYER TESTING")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Criar e executar suite
        suite, test_classes = self.create_services_test_suite()
        
        # Executar cada service separadamente para relatório detalhado
        overall_success = True
        
        for service_name, test_class in test_classes:
            print(f"\n🔧 Testando {service_name}...")
            print("-" * 50)
            
            # Criar suite apenas para este service
            service_suite = unittest.makeSuite(test_class)
            
            # Capturar saída para processar depois
            stream = StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(service_suite)
            
            # Processar resultado
            self._process_service_result(service_name, result)
            
            if not result.wasSuccessful():
                overall_success = False
        
        # Relatório final
        self._print_final_report(overall_success)
        
        return overall_success
    
    def run_specific_service_test(self, service_name):
        """Executa testes de um service específico"""
        service_map = {
            'account': ('AccountService', TestAccountService),
            'card': ('CardService', TestCardService),
            'transaction': ('TransactionService', TestTransactionService),
            'period': ('PeriodService', TestPeriodService),
            'alzi': ('AlziService', TestAlziService),
            'finance': ('FinanceService', TestFinanceService)
        }
        
        if service_name.lower() not in service_map:
            print(f"❌ Service '{service_name}' não encontrado.")
            print("Services disponíveis: account, card, transaction, period, alzi, finance")
            return False
        
        service_display_name, test_class = service_map[service_name.lower()]
        
        print(f"🧪 Executando testes do {service_display_name}...")
        print("=" * 60)
        
        # Executar testes
        suite = unittest.makeSuite(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Relatório específico
        print(f"\n📊 RELATÓRIO - {service_display_name}:")
        print(f"✅ Testes executados: {result.testsRun}")
        print(f"❌ Falhas: {len(result.failures)}")
        print(f"🚨 Erros: {len(result.errors)}")
        print(f"⏭️ Pulados: {len(result.skipped)}")
        
        if result.wasSuccessful():
            print(f"\n🎉 TODOS OS TESTES DO {service_display_name.upper()} PASSARAM!")
        else:
            print(f"\n❌ ALGUNS TESTES DO {service_display_name.upper()} FALHARAM!")
            if result.failures:
                print("\n🔍 Falhas encontradas:")
                for test, traceback in result.failures:
                    print(f"  - {test}")
            if result.errors:
                print("\n🚨 Erros encontrados:")
                for test, traceback in result.errors:
                    print(f"  - {test}")
        
        return result.wasSuccessful()
    
    def run_integration_tests(self):
        """Executa testes de integração entre services"""
        print("🔗 Executando testes de integração entre services...")
        print("=" * 60)
        
        # Por enquanto, apenas validamos que todos os services funcionam juntos
        # Futuramente, podemos adicionar testes de integração específicos
        
        # Teste básico: importar todos os services
        try:
            from modules.finances.services import (
                AccountService, CardService, TransactionService,
                PeriodService, AlziService, FinanceService
            )
            print("✅ Todos os services foram importados com sucesso")
            
            # Teste básico: criar instância do FinanceService
            # (que internamente cria todos os outros)
            finance_service = FinanceService()
            print("✅ FinanceService criado com sucesso (orquestra todos os services)")
            
            print("\n🎉 TESTES DE INTEGRAÇÃO PASSARAM!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na integração: {e}")
            print("\n❌ TESTES DE INTEGRAÇÃO FALHARAM!")
            return False
    
    def _process_service_result(self, service_name, result):
        """Processa resultado de um service"""
        self.results[service_name] = {
            'tests': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'success': result.wasSuccessful()
        }
        
        # Atualizar totais
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)
        self.total_skipped += len(result.skipped)
        
        # Imprimir resultado do service
        status = "✅ PASSOU" if result.wasSuccessful() else "❌ FALHOU"
        print(f"   {status} - {result.testsRun} testes, {len(result.failures)} falhas, {len(result.errors)} erros")
    
    def _print_final_report(self, overall_success):
        """Imprime relatório final detalhado"""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - SERVICES LAYER TESTS")
        print("=" * 80)
        
        # Estatísticas gerais
        print(f"⏱️  Tempo de execução: {elapsed_time:.2f} segundos")
        print(f"📋 Total de testes: {self.total_tests}")
        print(f"✅ Sucessos: {self.total_tests - self.total_failures - self.total_errors}")
        print(f"❌ Falhas: {self.total_failures}")
        print(f"🚨 Erros: {self.total_errors}")
        print(f"⏭️ Pulados: {self.total_skipped}")
        
        # Resultado por service
        print(f"\n📊 Resultados por Service:")
        print("-" * 60)
        for service_name, stats in self.results.items():
            status = "✅" if stats['success'] else "❌"
            print(f"{status} {service_name:<18} - {stats['tests']:>2} testes, "
                  f"{stats['failures']:>2} falhas, {stats['errors']:>2} erros")
        
        # Status final
        print("\n" + "=" * 80)
        if overall_success:
            print("🎉 TODOS OS TESTES DOS SERVICES PASSARAM!")
            print("✅ Services Layer está funcionando perfeitamente")
            print("✅ Lógica de negócios validada")
            print("✅ Integração entre domains e services confirmada")
            print("✅ Pronto para Fase 3 da refatoração")
        else:
            print("❌ ALGUNS TESTES DOS SERVICES FALHARAM!")
            print("🔍 Verifique os erros acima para correção")
            print("⚠️ Services Layer precisa de ajustes antes da Fase 3")
        
        print("=" * 80)


def main():
    """Função principal"""
    runner = ServiceTestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'integration':
            # Executar apenas testes de integração
            success = runner.run_integration_tests()
        elif command in ['account', 'card', 'transaction', 'period', 'alzi', 'finance']:
            # Executar teste específico
            success = runner.run_specific_service_test(command)
        elif command == 'help':
            print("🧪 SERVICE TESTS RUNNER")
            print("=" * 40)
            print("Uso:")
            print("  python run_services_tests.py              # Executar todos os testes")
            print("  python run_services_tests.py <service>    # Executar service específico")
            print("  python run_services_tests.py integration  # Executar testes de integração")
            print("  python run_services_tests.py help         # Mostrar esta ajuda")
            print("\nServices disponíveis:")
            print("  - account      (AccountService)")
            print("  - card         (CardService)")
            print("  - transaction  (TransactionService)")
            print("  - period       (PeriodService)")
            print("  - alzi         (AlziService)")
            print("  - finance      (FinanceService)")
            return
        else:
            print(f"❌ Comando '{command}' não reconhecido.")
            print("Use 'help' para ver opções disponíveis.")
            return
    else:
        # Executar todos os testes
        success = runner.run_all_services_tests()
        
        # Executar testes de integração também
        print("\n")
        integration_success = runner.run_integration_tests()
        
        success = success and integration_success
    
    # Exit code para CI/CD
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()