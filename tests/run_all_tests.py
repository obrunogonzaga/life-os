"""
Script para executar todos os testes unitários dos domains

Este script executa todos os testes dos 5 domains criados na Fase 1
da refatoração do módulo finances.
"""

import unittest
import sys
import os

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar todos os testes
from test_account_domain import TestAccountDomain
from test_card_domain import TestCardDomain
from test_transaction_domain import TestTransactionDomain
from test_alzi_domain import TestAlziDomain
from test_period_domain import TestPeriodDomain


def create_test_suite():
    """Cria suite com todos os testes"""
    suite = unittest.TestSuite()
    
    # Adicionar todos os testes
    suite.addTest(unittest.makeSuite(TestAccountDomain))
    suite.addTest(unittest.makeSuite(TestCardDomain))
    suite.addTest(unittest.makeSuite(TestTransactionDomain))
    suite.addTest(unittest.makeSuite(TestAlziDomain))
    suite.addTest(unittest.makeSuite(TestPeriodDomain))
    
    return suite


def run_tests():
    """Executa todos os testes com relatório detalhado"""
    print("🧪 Executando testes unitários dos domains...")
    print("=" * 60)
    
    # Criar e executar suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL:")
    print(f"✅ Testes executados: {result.testsRun}")
    print(f"❌ Falhas: {len(result.failures)}")
    print(f"🚨 Erros: {len(result.errors)}")
    print(f"⏭️ Pulados: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Domains estão funcionando perfeitamente")
        print("✅ Regras de negócio validadas")
        print("✅ Pronto para Fase 2 da refatoração")
        return True
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        if result.failures:
            print("\nFalhas encontradas:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        if result.errors:
            print("\nErros encontrados:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        return False


def run_individual_test(domain_name):
    """Executa testes de um domain específico"""
    test_classes = {
        'account': TestAccountDomain,
        'card': TestCardDomain,
        'transaction': TestTransactionDomain,
        'alzi': TestAlziDomain,
        'period': TestPeriodDomain
    }
    
    if domain_name.lower() not in test_classes:
        print(f"❌ Domain '{domain_name}' não encontrado.")
        print("Domains disponíveis: account, card, transaction, alzi, period")
        return False
    
    test_class = test_classes[domain_name.lower()]
    suite = unittest.makeSuite(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Executar teste específico
        domain = sys.argv[1]
        print(f"🧪 Executando testes do {domain.upper()}Domain...")
        success = run_individual_test(domain)
    else:
        # Executar todos os testes
        success = run_tests()
    
    # Exit code para CI/CD
    sys.exit(0 if success else 1)