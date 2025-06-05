#!/usr/bin/env python3
"""
Utilitário para testar conexão MongoDB com strings personalizadas
Localização: utils/test_connection.py
"""
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from datetime import datetime


def test_mongodb_connection(connection_string: str, timeout: int = 5) -> dict:
    """
    Testa conexão MongoDB com string fornecida
    
    Args:
        connection_string: String de conexão MongoDB
        timeout: Timeout em segundos para a conexão
        
    Returns:
        Dicionário com resultados do teste
    """
    result = {
        "success": False,
        "connection_string": connection_string,
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "errors": [],
        "server_info": {}
    }
    
    client = None
    
    try:
        print(f"🔗 Testando conexão MongoDB...")
        print(f"⏱️  Timeout: {timeout}s")
        print(f"🌐 String: {connection_string[:50]}{'...' if len(connection_string) > 50 else ''}")
        print()
        
        # 1. Teste de Conexão Básica
        print("1️⃣ Testando conexão básica...")
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=timeout * 1000,
            connectTimeoutMS=timeout * 1000,
            socketTimeoutMS=timeout * 1000
        )
        
        # 2. Teste de Ping
        print("2️⃣ Testando ping...")
        client.admin.command('ping')
        result["tests"]["ping"] = True
        print("   ✅ Ping bem-sucedido")
        
        # 3. Informações do Servidor
        print("3️⃣ Obtendo informações do servidor...")
        server_info = client.server_info()
        result["server_info"] = {
            "version": server_info.get("version"),
            "git_version": server_info.get("gitVersion"),
            "platform": server_info.get("sysInfo", "").split(" ")[0] if server_info.get("sysInfo") else "unknown"
        }
        result["tests"]["server_info"] = True
        print(f"   ✅ MongoDB v{server_info.get('version', 'unknown')}")
        
        # 4. Teste de Listagem de Bancos
        print("4️⃣ Testando listagem de bancos...")
        try:
            databases = client.list_database_names()
            result["tests"]["list_databases"] = True
            result["server_info"]["databases"] = databases
            print(f"   ✅ {len(databases)} bancos encontrados: {', '.join(databases[:3])}{'...' if len(databases) > 3 else ''}")
        except Exception as e:
            result["tests"]["list_databases"] = False
            print(f"   ⚠️  Sem permissão para listar bancos: {e}")
        
        # 5. Teste de Operações no Banco Específico
        print("5️⃣ Testando operações no banco de dados...")
        try:
            # Extrair nome do banco da string de conexão
            db_name = "lifeos"  # padrão
            if "/" in connection_string:
                parts = connection_string.split("/")
                if len(parts) > 3:
                    db_part = parts[-1]
                    if "?" in db_part:
                        db_name = db_part.split("?")[0]
                    else:
                        db_name = db_part
            
            db = client[db_name]
            
            # Teste de inserção/consulta
            test_collection = db["connection_test"]
            test_doc = {"test": "connection", "timestamp": datetime.now()}
            
            # Inserir documento de teste
            insert_result = test_collection.insert_one(test_doc)
            result["tests"]["insert"] = True
            print(f"   ✅ Inserção bem-sucedida: {insert_result.inserted_id}")
            
            # Consultar documento
            found_doc = test_collection.find_one({"_id": insert_result.inserted_id})
            result["tests"]["query"] = True
            print(f"   ✅ Consulta bem-sucedida")
            
            # Limpar documento de teste
            test_collection.delete_one({"_id": insert_result.inserted_id})
            result["tests"]["delete"] = True
            print(f"   ✅ Remoção bem-sucedida")
            
            result["server_info"]["target_database"] = db_name
            
        except Exception as e:
            result["tests"]["database_operations"] = False
            result["errors"].append(f"Erro em operações do banco: {e}")
            print(f"   ⚠️  Erro em operações do banco: {e}")
        
        # 6. Teste de Índices (se Life OS collections existem)
        print("6️⃣ Verificando collections do Life OS...")
        try:
            collections = db.list_collection_names()
            lifeos_collections = [c for c in collections if c in ["news_articles", "news_metadata", "article_details"]]
            
            if lifeos_collections:
                result["tests"]["lifeos_collections"] = True
                result["server_info"]["lifeos_collections"] = lifeos_collections
                print(f"   ✅ Collections do Life OS encontradas: {', '.join(lifeos_collections)}")
                
                # Contar documentos
                for collection_name in lifeos_collections:
                    count = db[collection_name].count_documents({})
                    print(f"      📄 {collection_name}: {count} documentos")
            else:
                result["tests"]["lifeos_collections"] = False
                print(f"   ℹ️  Nenhuma collection do Life OS encontrada (banco novo)")
                
        except Exception as e:
            result["tests"]["lifeos_collections"] = False
            print(f"   ⚠️  Erro ao verificar collections: {e}")
        
        result["success"] = True
        print("\n🎉 Teste de conexão CONCLUÍDO COM SUCESSO!")
        
    except ConnectionFailure as e:
        result["errors"].append(f"Falha de conexão: {e}")
        print(f"\n❌ FALHA DE CONEXÃO: {e}")
        
    except ServerSelectionTimeoutError as e:
        result["errors"].append(f"Timeout de conexão: {e}")
        print(f"\n⏰ TIMEOUT DE CONEXÃO: {e}")
        print("   💡 Verifique: host, porta, firewall, conectividade de rede")
        
    except OperationFailure as e:
        if "authentication" in str(e).lower():
            result["errors"].append(f"Falha de autenticação: {e}")
            print(f"\n🔐 FALHA DE AUTENTICAÇÃO: {e}")
            print("   💡 Verifique: usuário, senha, authSource")
        else:
            result["errors"].append(f"Falha de operação: {e}")
            print(f"\n⚠️  FALHA DE OPERAÇÃO: {e}")
            
    except Exception as e:
        result["errors"].append(f"Erro inesperado: {e}")
        print(f"\n💥 ERRO INESPERADO: {e}")
        
    finally:
        if client:
            client.close()
            print("🔌 Conexão fechada")
    
    return result


def main():
    """
    Função principal para teste interativo
    """
    print("=" * 60)
    print("🧪 TESTADOR DE CONEXÃO MONGODB - LIFE OS")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # String passada como argumento
        connection_string = sys.argv[1]
    else:
        # Solicitar string interativamente
        print("\nDigite a string de conexão MongoDB:")
        print("Exemplo: mongodb://user:pass@host:27017/database")
        connection_string = input("Connection String: ").strip()
    
    if not connection_string:
        print("❌ String de conexão não fornecida!")
        sys.exit(1)
    
    # Executar teste
    result = test_mongodb_connection(connection_string)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    
    if result["success"]:
        print("🎯 Status: ✅ SUCESSO")
    else:
        print("🎯 Status: ❌ FALHA")
    
    print(f"🕐 Timestamp: {result['timestamp']}")
    
    if result["server_info"]:
        print(f"🖥️  Servidor: MongoDB v{result['server_info'].get('version', 'unknown')}")
        if "target_database" in result["server_info"]:
            print(f"🗄️  Database: {result['server_info']['target_database']}")
    
    print("\n📋 Testes executados:")
    for test_name, success in result["tests"].items():
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    if result["errors"]:
        print("\n🚨 Erros encontrados:")
        for error in result["errors"]:
            print(f"   ❌ {error}")
    
    print("\n" + "=" * 60)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())