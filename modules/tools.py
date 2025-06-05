"""
Módulo de Ferramentas do Life OS
Inclui ferramentas de gerenciamento e utilitários diversos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from utils.database_manager import DatabaseManager
from utils.config import Config
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

console = Console()

class MongoDBTool:
    """Ferramenta de gerenciamento MongoDB"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.config = Config()
    
    def show_connection_status(self):
        """Mostra status da conexão MongoDB"""
        console.print("\n[bold blue]📊 Status da Conexão MongoDB[/bold blue]")
        
        if self.db_manager.is_connected():
            # Determinar se é local ou remoto
            if self.config.DATABASE_MODE == "remote":
                host = self.config.REMOTE_MONGODB_HOST or "N/A"
                port = str(self.config.REMOTE_MONGODB_PORT)
                database = self.config.REMOTE_MONGODB_DATABASE
                is_local = False
            else:
                host = self.config.MONGODB_HOST
                port = str(self.config.MONGODB_PORT)
                database = self.config.MONGODB_DATABASE
                is_local = host in ['localhost', '127.0.0.1', '::1']
            
            status_table = Table(show_header=True, header_style="bold magenta")
            status_table.add_column("Propriedade", style="cyan")
            status_table.add_column("Valor", style="green")
            
            status_table.add_row("Status", "✅ Conectado")
            status_table.add_row("Tipo", "🏠 Local" if is_local else "🌐 Remoto")
            status_table.add_row("Host", host)
            status_table.add_row("Porta", port)
            status_table.add_row("Database", database)
            
            # Tentar obter informações do servidor
            try:
                server_info = self.db_manager.db.client.server_info()
                status_table.add_row("Versão MongoDB", server_info.get('version', 'N/A'))
            except:
                pass
                
            console.print(status_table)
        else:
            console.print("❌ [red]MongoDB não conectado - usando fallback JSON[/red]")
    
    def list_collections(self):
        """Lista todas as collections disponíveis"""
        console.print("\n[bold blue]📁 Collections Disponíveis[/bold blue]")
        
        if not self.db_manager.is_connected():
            console.print("❌ [red]MongoDB não disponível[/red]")
            return
        
        try:
            collections = self.db_manager.db.list_collection_names()
            
            if not collections:
                console.print("📭 [yellow]Nenhuma collection encontrada[/yellow]")
                return
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Collection", style="cyan")
            table.add_column("Documentos", style="green")
            table.add_column("Tamanho Aprox.", style="yellow")
            
            for collection_name in collections:
                try:
                    collection = self.db_manager.db[collection_name]
                    count = collection.count_documents({})
                    
                    # Estimar tamanho
                    stats = self.db_manager.db.command("collStats", collection_name)
                    size = stats.get('size', 0)
                    size_str = self._format_bytes(size)
                    
                    table.add_row(collection_name, str(count), size_str)
                except Exception as e:
                    table.add_row(collection_name, "Erro", str(e)[:20])
            
            console.print(table)
            
        except Exception as e:
            console.print(f"❌ [red]Erro ao listar collections: {e}[/red]")
    
    def collection_details(self, collection_name: str):
        """Mostra detalhes de uma collection específica"""
        console.print(f"\n[bold blue]📊 Detalhes da Collection: {collection_name}[/bold blue]")
        
        if not self.db_manager.is_connected():
            console.print("❌ [red]MongoDB não disponível[/red]")
            return
        
        try:
            collection = self.db_manager.db[collection_name]
            
            # Estatísticas básicas
            stats_table = Table(show_header=True, header_style="bold magenta")
            stats_table.add_column("Propriedade", style="cyan")
            stats_table.add_column("Valor", style="green")
            
            count = collection.count_documents({})
            stats_table.add_row("Total de Documentos", str(count))
            
            if count > 0:
                # Estatísticas da collection
                try:
                    stats = self.db_manager.db.command("collStats", collection_name)
                    stats_table.add_row("Tamanho", self._format_bytes(stats.get('size', 0)))
                    stats_table.add_row("Índices", str(stats.get('nindexes', 0)))
                    stats_table.add_row("Tamanho dos Índices", self._format_bytes(stats.get('totalIndexSize', 0)))
                except:
                    pass
                
                # Último documento inserido (aproximação)
                try:
                    last_doc = collection.find().sort("_id", -1).limit(1).next()
                    if '_id' in last_doc:
                        # Extrair timestamp do ObjectId
                        timestamp = last_doc['_id'].generation_time
                        stats_table.add_row("Último Documento", timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                except:
                    pass
            
            console.print(stats_table)
            
            # Mostrar alguns documentos de exemplo
            if count > 0:
                self._show_sample_documents(collection, collection_name)
                
        except Exception as e:
            console.print(f"❌ [red]Erro ao obter detalhes: {e}[/red]")
    
    def search_documents(self, collection_name: str, search_term: str, limit: int = 10):
        """Busca documentos em uma collection"""
        console.print(f"\n[bold blue]🔍 Busca em {collection_name}: '{search_term}'[/bold blue]")
        
        if not self.db_manager.is_connected():
            console.print("❌ [red]MongoDB não disponível[/red]")
            return
        
        try:
            collection = self.db_manager.db[collection_name]
            
            # Busca por texto em todos os campos string
            query = {
                "$or": [
                    {"titulo": {"$regex": search_term, "$options": "i"}},
                    {"conteudo": {"$regex": search_term, "$options": "i"}},
                    {"autor": {"$regex": search_term, "$options": "i"}},
                    {"link": {"$regex": search_term, "$options": "i"}},
                ]
            }
            
            docs = list(collection.find(query).limit(limit))
            
            if not docs:
                console.print("📭 [yellow]Nenhum documento encontrado[/yellow]")
                return
            
            console.print(f"✅ [green]Encontrados {len(docs)} documento(s)[/green]")
            
            for i, doc in enumerate(docs, 1):
                self._display_document_summary(doc, i)
                
        except Exception as e:
            console.print(f"❌ [red]Erro na busca: {e}[/red]")
    
    def recent_documents(self, collection_name: str, limit: int = 5):
        """Mostra documentos mais recentes"""
        console.print(f"\n[bold blue]⏰ Documentos Recentes em {collection_name}[/bold blue]")
        
        if not self.db_manager.is_connected():
            console.print("❌ [red]MongoDB não disponível[/red]")
            return
        
        try:
            collection = self.db_manager.db[collection_name]
            docs = list(collection.find().sort("_id", -1).limit(limit))
            
            if not docs:
                console.print("📭 [yellow]Nenhum documento encontrado[/yellow]")
                return
            
            for i, doc in enumerate(docs, 1):
                self._display_document_summary(doc, i)
                
        except Exception as e:
            console.print(f"❌ [red]Erro ao buscar documentos: {e}[/red]")
    
    def _show_sample_documents(self, collection, collection_name: str, limit: int = 3):
        """Mostra documentos de exemplo"""
        console.print(f"\n[bold yellow]📄 Exemplos de Documentos ({limit} primeiros):[/bold yellow]")
        
        try:
            docs = list(collection.find().limit(limit))
            for i, doc in enumerate(docs, 1):
                self._display_document_summary(doc, i)
        except Exception as e:
            console.print(f"❌ [red]Erro ao obter exemplos: {e}[/red]")
    
    def _display_document_summary(self, doc: Dict[Any, Any], index: int):
        """Exibe resumo de um documento"""
        try:
            # Remover _id para exibição mais limpa
            display_doc = {k: v for k, v in doc.items() if k != '_id'}
            
            # Truncar campos muito longos
            for key, value in display_doc.items():
                if isinstance(value, str) and len(value) > 100:
                    display_doc[key] = value[:100] + "..."
            
            # Criar painel com o documento
            doc_text = json.dumps(display_doc, ensure_ascii=False, indent=2, default=str)
            panel = Panel(
                doc_text,
                title=f"[bold cyan]Documento {index}[/bold cyan]",
                title_align="left",
                border_style="blue"
            )
            console.print(panel)
            
        except Exception as e:
            console.print(f"❌ [red]Erro ao exibir documento {index}: {e}[/red]")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Formata bytes em unidades legíveis"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"

class ToolsModule:
    """Módulo principal de ferramentas"""
    
    def __init__(self):
        self.mongodb_tool = MongoDBTool()
    
    def run(self):
        """Interface principal do módulo de ferramentas"""
        while True:
            self._show_main_menu()
            choice = console.input("\n[bold yellow]Escolha uma opção: [/bold yellow]").strip()
            
            if choice == "1":
                self._mongodb_menu()
            elif choice.upper() == "M":
                break
            else:
                console.print("❌ [red]Opção inválida[/red]")
    
    def _show_main_menu(self):
        """Mostra menu principal de ferramentas"""
        console.clear()
        
        title = Text("🔧 FERRAMENTAS", style="bold blue")
        console.print(Panel(title, expand=False, border_style="blue"))
        
        console.print("\n[bold cyan]Ferramentas Disponíveis:[/bold cyan]")
        console.print("1. 🗄️  Gerenciador MongoDB")
        console.print("\n[dim]M. Voltar ao Menu Principal[/dim]")
    
    def _mongodb_menu(self):
        """Menu do gerenciador MongoDB"""
        while True:
            console.clear()
            
            title = Text("🗄️ GERENCIADOR MONGODB", style="bold blue")
            console.print(Panel(title, expand=False, border_style="blue"))
            
            console.print("\n[bold cyan]Opções Disponíveis:[/bold cyan]")
            console.print("1. 📊 Status da Conexão")
            console.print("2. 📁 Listar Collections")
            console.print("3. 🔍 Detalhes de Collection")
            console.print("4. 🔎 Buscar Documentos")
            console.print("5. ⏰ Documentos Recentes")
            console.print("\n[dim]M. Voltar ao Menu de Ferramentas[/dim]")
            
            choice = console.input("\n[bold yellow]Escolha uma opção: [/bold yellow]").strip()
            
            if choice == "1":
                self.mongodb_tool.show_connection_status()
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            
            elif choice == "2":
                self.mongodb_tool.list_collections()
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            
            elif choice == "3":
                collection_name = console.input("\n[bold yellow]Nome da collection: [/bold yellow]").strip()
                if collection_name:
                    self.mongodb_tool.collection_details(collection_name)
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            
            elif choice == "4":
                collection_name = console.input("\n[bold yellow]Nome da collection: [/bold yellow]").strip()
                if collection_name:
                    search_term = console.input("[bold yellow]Termo de busca: [/bold yellow]").strip()
                    if search_term:
                        limit = console.input("[bold yellow]Limite de resultados (padrão 10): [/bold yellow]").strip()
                        limit = int(limit) if limit.isdigit() else 10
                        self.mongodb_tool.search_documents(collection_name, search_term, limit)
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            
            elif choice == "5":
                collection_name = console.input("\n[bold yellow]Nome da collection: [/bold yellow]").strip()
                if collection_name:
                    limit = console.input("[bold yellow]Quantidade de documentos (padrão 5): [/bold yellow]").strip()
                    limit = int(limit) if limit.isdigit() else 5
                    self.mongodb_tool.recent_documents(collection_name, limit)
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            
            elif choice.upper() == "M":
                break
            
            else:
                console.print("❌ [red]Opção inválida[/red]")
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")

def main():
    """Função principal para testes"""
    tools = ToolsModule()
    tools.run()

if __name__ == "__main__":
    main()