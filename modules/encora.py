#!/usr/bin/env python3
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from typing import List, Optional, Dict
import os
import sys
from datetime import datetime, timedelta
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager

console = Console()


class EncoraModule:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.fallback_file = "data/encora_data.json"
        
        # Collections do MongoDB
        self.collections = {
            'ponto_registros': 'encora_ponto_registros',
            'notas': 'encora_notas',
            'projetos': 'encora_projetos',
            'metas': 'encora_metas',
            'configuracoes': 'encora_configuracoes'
        }
        
        self.ensure_fallback_file()
        self.ensure_default_configurations()
    
    def ensure_fallback_file(self):
        """Garante que o arquivo de fallback existe"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.fallback_file):
            initial_data = {
                "ponto": {"registros": [], "configuracoes": {}},
                "notas": [],
                "projetos": [],
                "metas": []
            }
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def ensure_default_configurations(self):
        """Garante que as configurações padrão existem"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['configuracoes'])
            existing = collection.find_one({"tipo": "ponto"})
            
            if not existing:
                default_config = {
                    "tipo": "ponto",
                    "carga_horaria_diaria": 8,
                    "horario_almoco": "12:00-13:00",
                    "created_at": datetime.now()
                }
                collection.insert_one(default_config)
    
    def get_configuracoes_ponto(self) -> Dict:
        """Obtém configurações do ponto"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['configuracoes'])
            config = collection.find_one({"tipo": "ponto"})
            if config:
                return config
        
        # Fallback
        return {
            "carga_horaria_diaria": 8,
            "horario_almoco": "12:00-13:00"
        }
    
    def _get_registros_ponto_por_data(self, data: str) -> List[Dict]:
        """Obtém registros de ponto por data"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['ponto_registros'])
            registros = list(collection.find({"data": data}).sort("timestamp", 1))
            return registros
        
        # Fallback para arquivo JSON
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
                return [r for r in data_json.get("ponto", {}).get("registros", []) if r.get("data") == data]
        except:
            return []
    
    def _get_todos_registros_ponto(self) -> List[Dict]:
        """Obtém todos os registros de ponto"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['ponto_registros'])
            registros = list(collection.find().sort("timestamp", 1))
            return registros
        
        # Fallback para arquivo JSON
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
                return data_json.get("ponto", {}).get("registros", [])
        except:
            return []
    
    def _salvar_registro_ponto(self, registro: Dict):
        """Salva registro de ponto"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['ponto_registros'])
            collection.insert_one(registro)
        else:
            # Fallback para arquivo JSON
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    data_json = json.load(f)
                
                data_json.setdefault("ponto", {}).setdefault("registros", []).append(registro)
                
                with open(self.fallback_file, 'w', encoding='utf-8') as f:
                    json.dump(data_json, f, indent=2, ensure_ascii=False)
            except Exception as e:
                console.print(f"[red]Erro ao salvar no fallback: {e}[/red]")
    
    def _get_notas(self) -> List[Dict]:
        """Obtém todas as notas"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['notas'])
            notas = list(collection.find().sort("created_at", -1))
            return notas
        
        # Fallback para arquivo JSON
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
                return data_json.get("notas", [])
        except:
            return []
    
    def _salvar_nota(self, nota: Dict):
        """Salva uma nota"""
        if self.db_manager.is_connected():
            collection = self.db_manager.get_collection(self.collections['notas'])
            result = collection.insert_one(nota)
            nota['_id'] = result.inserted_id
        else:
            # Fallback para arquivo JSON
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    data_json = json.load(f)
                
                data_json.setdefault("notas", []).append(nota)
                
                with open(self.fallback_file, 'w', encoding='utf-8') as f:
                    json.dump(data_json, f, indent=2, ensure_ascii=False)
            except Exception as e:
                console.print(f"[red]Erro ao salvar nota no fallback: {e}[/red]")
    
    def _excluir_nota(self, nota_id: str):
        """Exclui uma nota"""
        if self.db_manager.is_connected():
            from bson.objectid import ObjectId
            collection = self.db_manager.get_collection(self.collections['notas'])
            try:
                result = collection.delete_one({"_id": ObjectId(nota_id)})
                return result.deleted_count > 0
            except:
                # Tenta buscar por ID numérico
                result = collection.delete_one({"id": int(nota_id)})
                return result.deleted_count > 0
        else:
            # Fallback para arquivo JSON
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    data_json = json.load(f)
                
                notas = data_json.get("notas", [])
                for i, nota in enumerate(notas):
                    if str(nota.get("id")) == str(nota_id):
                        del notas[i]
                        with open(self.fallback_file, 'w', encoding='utf-8') as f:
                            json.dump(data_json, f, indent=2, ensure_ascii=False)
                        return True
                return False
            except:
                return False
    
    def run(self):
        """Menu principal do módulo Encora"""
        while True:
            console.clear()
            self._display_header()
            self._display_main_menu()
            
            choice = Prompt.ask("Escolha uma opção", default="1")
            
            if choice == "1":
                self._controle_ponto_menu()
            elif choice == "2":
                self._notas_menu()
            elif choice == "3":
                self._projetos_menu()
            elif choice == "4":
                self._metas_menu()
            elif choice == "5":
                self._dashboard()
            elif choice == "0" or choice.upper() == "M":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _display_header(self):
        """Exibe cabeçalho do módulo"""
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        console.print(Panel.fit(
            f"[bold blue]🏢 ENCORA WORKSPACE[/bold blue]\n"
            f"[dim]Ferramentas para o trabalho[/dim]\n"
            f"[dim]{current_date} • {current_time}[/dim]",
            border_style="blue"
        ))
        console.print()
    
    def _display_main_menu(self):
        """Exibe menu principal"""
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("Opção", style="cyan", width=8)
        table.add_column("Módulo", style="white")
        table.add_column("Descrição", style="dim")
        
        table.add_row("1", "⏰ Ponto", "Controle de horários e jornada")
        table.add_row("2", "📝 Notas", "Anotações e lembretes")
        table.add_row("3", "📁 Projetos", "Projetos e entregas")
        table.add_row("4", "🎯 Metas", "Objetivos e KPIs")
        table.add_row("5", "📊 Dashboard", "Visão geral do trabalho")
        table.add_row("", "", "")
        table.add_row("0/M", "🔙 Voltar", "Menu principal do Life OS")
        
        console.print(table)
        console.print()
    
    def _controle_ponto_menu(self):
        """Menu de controle de ponto"""
        while True:
            console.clear()
            self._display_header()
            console.print(Panel("⏰ CONTROLE DE PONTO", style="cyan"))
            
            # Exibe status do dia atual
            hoje = datetime.now().strftime("%Y-%m-%d")
            registros_hoje = self._get_registros_ponto_por_data(hoje)
            
            if registros_hoje:
                ultimo_registro = registros_hoje[-1]
                status = "🟢 Trabalhando" if ultimo_registro["tipo"] == "entrada" else "🔴 Pausado"
                console.print(f"\n[bold]Status atual: {status}[/bold]")
                console.print(f"Último registro: {ultimo_registro['horario']} ({ultimo_registro['tipo']})")
            else:
                console.print("\n[yellow]Nenhum registro hoje[/yellow]")
            
            # Menu de opções
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Opção", style="cyan", width=8)
            table.add_column("Ação", style="white")
            
            table.add_row("1", "🕐 Registrar Entrada")
            table.add_row("2", "🕕 Registrar Saída")
            table.add_row("3", "🍽️ Início do Almoço")
            table.add_row("4", "🍽️ Fim do Almoço")
            table.add_row("5", "📋 Ver Registros de Hoje")
            table.add_row("6", "✏️ Editar Registro")
            table.add_row("7", "🗑️ Remover Registro")
            table.add_row("8", "📊 Relatório Semanal")
            table.add_row("9", "📈 Relatório Mensal")
            table.add_row("10", "⚙️ Configurações")
            table.add_row("0", "🔙 Voltar")
            
            console.print(table)
            console.print()
            
            choice = Prompt.ask("Escolha uma opção", default="1")
            
            if choice == "1":
                self._registrar_ponto("entrada")
            elif choice == "2":
                self._registrar_ponto("saida")
            elif choice == "3":
                self._registrar_ponto("inicio_almoco")
            elif choice == "4":
                self._registrar_ponto("fim_almoco")
            elif choice == "5":
                self._ver_registros_hoje()
            elif choice == "6":
                self._editar_registro_ponto()
            elif choice == "7":
                self._remover_registro_ponto()
            elif choice == "8":
                self._relatorio_semanal()
            elif choice == "9":
                self._relatorio_mensal()
            elif choice == "10":
                self._configuracoes_ponto()
            elif choice == "0":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _registrar_ponto(self, tipo: str):
        """Registra ponto"""
        agora = datetime.now()
        data = agora.strftime("%Y-%m-%d")
        horario = agora.strftime("%H:%M")
        
        tipos_nomes = {
            "entrada": "Entrada",
            "saida": "Saída",
            "inicio_almoco": "Início do Almoço",
            "fim_almoco": "Fim do Almoço"
        }
        
        registro = {
            "data": data,
            "horario": horario,
            "tipo": tipo,
            "timestamp": agora.isoformat(),
            "created_at": agora
        }
        
        self._salvar_registro_ponto(registro)
        
        console.print(f"\n[green]✅ {tipos_nomes[tipo]} registrada às {horario}[/green]")
        console.input("\nPressione Enter para continuar...")
    
    def _ver_registros_hoje(self, show_ids=False):
        """Exibe registros do dia atual"""
        console.clear()
        self._display_header()
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        registros_hoje = self._get_registros_ponto_por_data(hoje)
        
        if not registros_hoje:
            console.print("[yellow]Nenhum registro encontrado para hoje.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return registros_hoje
        
        table = Table(title=f"Registros de {datetime.now().strftime('%d/%m/%Y')}", box=box.ROUNDED)
        if show_ids:
            table.add_column("ID", style="dim", width=5)
        table.add_column("Horário", style="cyan")
        table.add_column("Tipo", style="white")
        
        tipos_nomes = {
            "entrada": "🕐 Entrada",
            "saida": "🕕 Saída",
            "inicio_almoco": "🍽️ Início Almoço",
            "fim_almoco": "🍽️ Fim Almoço"
        }
        
        for i, registro in enumerate(registros_hoje, 1):
            if show_ids:
                table.add_row(
                    str(i),
                    registro["horario"],
                    tipos_nomes.get(registro["tipo"], registro["tipo"])
                )
            else:
                table.add_row(
                    registro["horario"],
                    tipos_nomes.get(registro["tipo"], registro["tipo"])
                )
        
        console.print(table)
        if not show_ids:
            console.input("\nPressione Enter para continuar...")
        
        return registros_hoje
    
    def _editar_registro_ponto(self):
        """Editar registro de ponto"""
        console.clear()
        self._display_header()
        console.print(Panel("✏️ EDITAR REGISTRO DE PONTO", style="cyan"))
        
        # Perguntar se quer editar registros de hoje ou escolher data
        console.print("\n[bold]Escolha uma opção:[/bold]")
        console.print("1. Editar registros de hoje")
        console.print("2. Editar registros de outra data")
        
        escolha = Prompt.ask("Opção", default="1")
        
        if escolha == "1":
            data_escolhida = datetime.now().strftime("%Y-%m-%d")
        elif escolha == "2":
            # Permitir escolher data dentro do mês atual
            mes_atual = datetime.now().strftime("%m/%Y")
            data_str = Prompt.ask(f"Digite a data (DD/MM/YYYY) - Mês atual: {mes_atual}")
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                # Verificar se está no mês atual
                if data_obj.month != datetime.now().month or data_obj.year != datetime.now().year:
                    console.print("[yellow]⚠️ Só é permitido editar registros do mês atual![/yellow]")
                    console.input("\nPressione Enter para continuar...")
                    return
                data_escolhida = data_obj.strftime("%Y-%m-%d")
            except ValueError:
                console.print("[red]Data inválida![/red]")
                console.input("\nPressione Enter para continuar...")
                return
        else:
            return
        
        # Buscar registros da data escolhida
        registros = self._get_registros_ponto_por_data(data_escolhida)
        
        if not registros:
            console.print(f"\n[yellow]Nenhum registro encontrado para {datetime.strptime(data_escolhida, '%Y-%m-%d').strftime('%d/%m/%Y')}.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        # Exibir registros com IDs
        console.clear()
        self._display_header()
        
        table = Table(title=f"Registros de {datetime.strptime(data_escolhida, '%Y-%m-%d').strftime('%d/%m/%Y')}", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=5)
        table.add_column("Horário", style="cyan")
        table.add_column("Tipo", style="white")
        
        tipos_nomes = {
            "entrada": "🕐 Entrada",
            "saida": "🕕 Saída",
            "inicio_almoco": "🍽️ Início Almoço",
            "fim_almoco": "🍽️ Fim Almoço"
        }
        
        for i, registro in enumerate(registros, 1):
            table.add_row(
                str(i),
                registro["horario"],
                tipos_nomes.get(registro["tipo"], registro["tipo"])
            )
        
        console.print(table)
        
        console.print()
        id_registro = Prompt.ask("Número do registro para editar (0 para cancelar)")
        
        if id_registro == "0":
            return
        
        try:
            idx = int(id_registro) - 1
            if idx < 0 or idx >= len(registros):
                console.print("[red]Número de registro inválido![/red]")
                console.input("\nPressione Enter para continuar...")
                return
            
            registro = registros[idx]
            
            console.print(f"\n[bold]Editando registro:[/bold]")
            console.print(f"Horário atual: {registro['horario']}")
            console.print(f"Tipo atual: {registro['tipo']}")
            
            # Editar horário
            novo_horario = Prompt.ask("Novo horário (HH:MM)", default=registro['horario'])
            
            # Validar formato do horário
            try:
                datetime.strptime(novo_horario, "%H:%M")
            except ValueError:
                console.print("[red]Formato de horário inválido! Use HH:MM[/red]")
                console.input("\nPressione Enter para continuar...")
                return
            
            # Editar tipo
            tipos_validos = ["entrada", "saida", "inicio_almoco", "fim_almoco"]
            console.print("\nTipos válidos: entrada, saida, inicio_almoco, fim_almoco")
            novo_tipo = Prompt.ask("Novo tipo", default=registro['tipo'])
            
            if novo_tipo not in tipos_validos:
                console.print("[red]Tipo inválido![/red]")
                console.input("\nPressione Enter para continuar...")
                return
            
            # Confirmar edição
            if Confirm.ask("Confirma a edição do registro?"):
                # Atualizar registro
                if self.db_manager.is_connected():
                    collection = self.db_manager.get_collection(self.collections['ponto_registros'])
                    # Encontrar e atualizar o registro específico
                    collection.update_one(
                        {
                            "data": registro["data"],
                            "horario": registro["horario"],
                            "tipo": registro["tipo"]
                        },
                        {
                            "$set": {
                                "horario": novo_horario,
                                "tipo": novo_tipo,
                                "timestamp": datetime.strptime(f"{registro['data']} {novo_horario}", "%Y-%m-%d %H:%M").isoformat(),
                                "updated_at": datetime.now()
                            }
                        }
                    )
                    console.print(f"\n[green]✅ Registro atualizado com sucesso![/green]")
                else:
                    # Atualizar no fallback JSON
                    try:
                        with open(self.fallback_file, 'r', encoding='utf-8') as f:
                            data_json = json.load(f)
                        
                        registros = data_json.get("ponto", {}).get("registros", [])
                        for r in registros:
                            if (r.get("data") == registro["data"] and 
                                r.get("horario") == registro["horario"] and 
                                r.get("tipo") == registro["tipo"]):
                                r["horario"] = novo_horario
                                r["tipo"] = novo_tipo
                                r["timestamp"] = datetime.strptime(f"{registro['data']} {novo_horario}", "%Y-%m-%d %H:%M").isoformat()
                                r["updated_at"] = datetime.now().isoformat()
                                break
                        
                        with open(self.fallback_file, 'w', encoding='utf-8') as f:
                            json.dump(data_json, f, indent=2, ensure_ascii=False)
                        
                        console.print(f"\n[green]✅ Registro atualizado com sucesso![/green]")
                    except Exception as e:
                        console.print(f"[red]Erro ao atualizar registro: {e}[/red]")
                
                console.input("\nPressione Enter para continuar...")
        
        except ValueError:
            console.print("[red]Entrada inválida![/red]")
            console.input("\nPressione Enter para continuar...")
    
    def _remover_registro_ponto(self):
        """Remover registro de ponto"""
        console.clear()
        self._display_header()
        console.print(Panel("🗑️ REMOVER REGISTRO DE PONTO", style="red"))
        
        # Perguntar se quer remover registros de hoje ou escolher data
        console.print("\n[bold]Escolha uma opção:[/bold]")
        console.print("1. Remover registros de hoje")
        console.print("2. Remover registros de outra data")
        
        escolha = Prompt.ask("Opção", default="1")
        
        if escolha == "1":
            data_escolhida = datetime.now().strftime("%Y-%m-%d")
        elif escolha == "2":
            # Permitir escolher data dentro do mês atual
            mes_atual = datetime.now().strftime("%m/%Y")
            data_str = Prompt.ask(f"Digite a data (DD/MM/YYYY) - Mês atual: {mes_atual}")
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                # Verificar se está no mês atual
                if data_obj.month != datetime.now().month or data_obj.year != datetime.now().year:
                    console.print("[yellow]⚠️ Só é permitido remover registros do mês atual![/yellow]")
                    console.input("\nPressione Enter para continuar...")
                    return
                data_escolhida = data_obj.strftime("%Y-%m-%d")
            except ValueError:
                console.print("[red]Data inválida![/red]")
                console.input("\nPressione Enter para continuar...")
                return
        else:
            return
        
        # Buscar registros da data escolhida
        registros = self._get_registros_ponto_por_data(data_escolhida)
        
        if not registros:
            console.print(f"\n[yellow]Nenhum registro encontrado para {datetime.strptime(data_escolhida, '%Y-%m-%d').strftime('%d/%m/%Y')}.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        # Exibir registros com IDs
        console.clear()
        self._display_header()
        
        table = Table(title=f"Registros de {datetime.strptime(data_escolhida, '%Y-%m-%d').strftime('%d/%m/%Y')}", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=5)
        table.add_column("Horário", style="cyan")
        table.add_column("Tipo", style="white")
        
        tipos_nomes = {
            "entrada": "🕐 Entrada",
            "saida": "🕕 Saída",
            "inicio_almoco": "🍽️ Início Almoço",
            "fim_almoco": "🍽️ Fim Almoço"
        }
        
        for i, registro in enumerate(registros, 1):
            table.add_row(
                str(i),
                registro["horario"],
                tipos_nomes.get(registro["tipo"], registro["tipo"])
            )
        
        console.print(table)
        
        console.print()
        id_registro = Prompt.ask("Número do registro para remover (0 para cancelar)")
        
        if id_registro == "0":
            return
        
        try:
            idx = int(id_registro) - 1
            if idx < 0 or idx >= len(registros):
                console.print("[red]Número de registro inválido![/red]")
                console.input("\nPressione Enter para continuar...")
                return
            
            registro = registros[idx]
            
            console.print(f"\n[bold]Removendo registro:[/bold]")
            console.print(f"Horário: {registro['horario']}")
            console.print(f"Tipo: {registro['tipo']}")
            
            # Confirmar remoção
            if Confirm.ask("[bold red]Tem certeza que deseja remover este registro?[/bold red]"):
                # Remover registro
                if self.db_manager.is_connected():
                    collection = self.db_manager.get_collection(self.collections['ponto_registros'])
                    # Remover o registro específico
                    result = collection.delete_one({
                        "data": registro["data"],
                        "horario": registro["horario"],
                        "tipo": registro["tipo"]
                    })
                    
                    if result.deleted_count > 0:
                        console.print(f"\n[green]✅ Registro removido com sucesso![/green]")
                    else:
                        console.print(f"\n[red]Erro ao remover registro.[/red]")
                else:
                    # Remover do fallback JSON
                    try:
                        with open(self.fallback_file, 'r', encoding='utf-8') as f:
                            data_json = json.load(f)
                        
                        registros = data_json.get("ponto", {}).get("registros", [])
                        registros_filtrados = [
                            r for r in registros
                            if not (r.get("data") == registro["data"] and 
                                   r.get("horario") == registro["horario"] and 
                                   r.get("tipo") == registro["tipo"])
                        ]
                        
                        data_json["ponto"]["registros"] = registros_filtrados
                        
                        with open(self.fallback_file, 'w', encoding='utf-8') as f:
                            json.dump(data_json, f, indent=2, ensure_ascii=False)
                        
                        console.print(f"\n[green]✅ Registro removido com sucesso![/green]")
                    except Exception as e:
                        console.print(f"[red]Erro ao remover registro: {e}[/red]")
                
                console.input("\nPressione Enter para continuar...")
        
        except ValueError:
            console.print("[red]Entrada inválida![/red]")
            console.input("\nPressione Enter para continuar...")
    
    def _calcular_horas_trabalhadas(self, registros: List[Dict]) -> Dict:
        """Calcula horas trabalhadas baseado nos registros de ponto"""
        if not registros:
            return {
                'entrada': None,
                'saida': None,
                'inicio_almoco': None,
                'fim_almoco': None,
                'horas_trabalhadas': 0,
                'tempo_almoco': 0,
                'status': 'sem_registros'
            }
        
        # Organizar registros por tipo
        entradas = [r for r in registros if r['tipo'] == 'entrada']
        saidas = [r for r in registros if r['tipo'] == 'saida']
        inicio_almocos = [r for r in registros if r['tipo'] == 'inicio_almoco']
        fim_almocos = [r for r in registros if r['tipo'] == 'fim_almoco']
        
        result = {
            'entrada': entradas[0]['horario'] if entradas else None,
            'saida': saidas[-1]['horario'] if saidas else None,
            'inicio_almoco': inicio_almocos[0]['horario'] if inicio_almocos else None,
            'fim_almoco': fim_almocos[-1]['horario'] if fim_almocos else None,
            'horas_trabalhadas': 0,
            'tempo_almoco': 0,
            'status': 'incompleto'
        }
        
        # Calcular horas trabalhadas se tiver entrada e saída
        if result['entrada'] and result['saida']:
            try:
                entrada_time = datetime.strptime(result['entrada'], "%H:%M")
                saida_time = datetime.strptime(result['saida'], "%H:%M")
                
                # Lidar com saída no dia seguinte
                if saida_time < entrada_time:
                    saida_time += timedelta(days=1)
                
                total_tempo = saida_time - entrada_time
                horas_totais = total_tempo.total_seconds() / 3600
                
                # Calcular tempo de almoço
                tempo_almoco = 0
                if result['inicio_almoco'] and result['fim_almoco']:
                    inicio_almoco_time = datetime.strptime(result['inicio_almoco'], "%H:%M")
                    fim_almoco_time = datetime.strptime(result['fim_almoco'], "%H:%M")
                    
                    if fim_almoco_time > inicio_almoco_time:
                        almoco_delta = fim_almoco_time - inicio_almoco_time
                        tempo_almoco = almoco_delta.total_seconds() / 3600
                
                result['tempo_almoco'] = tempo_almoco
                result['horas_trabalhadas'] = max(0, horas_totais - tempo_almoco)
                result['status'] = 'completo'
                
            except ValueError:
                result['status'] = 'erro_calculo'
        
        return result
    
    def _relatorio_semanal(self):
        """Relatório semanal de ponto com tabela detalhada"""
        console.clear()
        self._display_header()
        console.print(Panel("📊 RELATÓRIO SEMANAL", style="cyan"))
        
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        config = self.get_configuracoes_ponto()
        carga_horaria_diaria = config.get('carga_horaria_diaria', 8)
        
        console.print(f"\n[bold]Período: {inicio_semana.strftime('%d/%m/%Y')} a {fim_semana.strftime('%d/%m/%Y')}[/bold]")
        
        # Tabela detalhada
        table = Table(title="Relatório Detalhado da Semana", box=box.ROUNDED)
        table.add_column("Data", style="cyan", width=12)
        table.add_column("Dia", style="white", width=10)
        table.add_column("Entrada", style="green", width=8)
        table.add_column("Saída", style="red", width=8)
        table.add_column("Almoço", style="yellow", width=12)
        table.add_column("Horas", style="magenta", width=8)
        table.add_column("Saldo", style="white", width=8)
        
        total_horas_trabalhadas = 0
        total_dias_trabalhados = 0
        dias_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB', 'DOM']
        
        for i in range(7):
            data_atual = inicio_semana + timedelta(days=i)
            data_str = data_atual.strftime("%Y-%m-%d")
            data_formatada = data_atual.strftime("%d/%m")
            dia_semana = dias_semana[i]
            
            registros_dia = self._get_registros_ponto_por_data(data_str)
            calculo = self._calcular_horas_trabalhadas(registros_dia)
            
            # Formatação dos dados
            entrada = calculo['entrada'] or '-'
            saida = calculo['saida'] or '-'
            
            almoco = '-'
            if calculo['inicio_almoco'] and calculo['fim_almoco']:
                almoco = f"{calculo['inicio_almoco']}-{calculo['fim_almoco']}"
            elif calculo['inicio_almoco']:
                almoco = f"{calculo['inicio_almoco']}-?"
            
            horas_str = f"{calculo['horas_trabalhadas']:.1f}h" if calculo['horas_trabalhadas'] > 0 else '-'
            
            # Calcular saldo (horas extras ou faltantes)
            saldo = 0
            saldo_str = '-'
            if calculo['horas_trabalhadas'] > 0:
                saldo = calculo['horas_trabalhadas'] - carga_horaria_diaria
                if saldo > 0:
                    saldo_str = f"+{saldo:.1f}h"
                elif saldo < 0:
                    saldo_str = f"{saldo:.1f}h"
                else:
                    saldo_str = "0h"
                
                total_horas_trabalhadas += calculo['horas_trabalhadas']
                total_dias_trabalhados += 1
            
            # Colorir linha baseado no status
            if data_atual > hoje:
                # Dia futuro
                style = "dim"
            elif calculo['status'] == 'sem_registros':
                style = "red dim"
            elif calculo['status'] == 'incompleto':
                style = "yellow"
            else:
                style = "white"
            
            table.add_row(
                data_formatada,
                dia_semana,
                entrada,
                saida,
                almoco,
                horas_str,
                saldo_str,
                style=style
            )
        
        console.print(table)
        
        # Resumo da semana
        horas_esperadas = total_dias_trabalhados * carga_horaria_diaria
        saldo_total = total_horas_trabalhadas - horas_esperadas
        
        resumo_table = Table(title="Resumo da Semana", box=box.ROUNDED)
        resumo_table.add_column("Métrica", style="cyan")
        resumo_table.add_column("Valor", style="white")
        
        resumo_table.add_row("Dias trabalhados", str(total_dias_trabalhados))
        resumo_table.add_row("Total de horas trabalhadas", f"{total_horas_trabalhadas:.1f}h")
        resumo_table.add_row("Horas esperadas", f"{horas_esperadas:.1f}h")
        
        if saldo_total > 0:
            resumo_table.add_row("Saldo", f"[green]+{saldo_total:.1f}h (extras)[/green]")
        elif saldo_total < 0:
            resumo_table.add_row("Saldo", f"[red]{saldo_total:.1f}h (faltantes)[/red]")
        else:
            resumo_table.add_row("Saldo", "0h (em dia)")
        
        console.print()
        console.print(resumo_table)
        
        console.input("\nPressione Enter para continuar...")
    
    def _relatorio_mensal(self):
        """Relatório mensal de ponto com tabela detalhada"""
        console.clear()
        self._display_header()
        console.print(Panel("📈 RELATÓRIO MENSAL", style="cyan"))
        
        hoje = datetime.now()
        primeiro_dia_mes = hoje.replace(day=1)
        
        # Calcular último dia do mês
        if hoje.month == 12:
            ultimo_dia_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
        
        config = self.get_configuracoes_ponto()
        carga_horaria_diaria = config.get('carga_horaria_diaria', 8)
        
        console.print(f"\n[bold]Período: {primeiro_dia_mes.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}[/bold]")
        
        # Tabela detalhada
        table = Table(title=f"Relatório Detalhado - {primeiro_dia_mes.strftime('%B/%Y')}", box=box.ROUNDED)
        table.add_column("Data", style="cyan", width=12)
        table.add_column("Dia", style="white", width=10)
        table.add_column("Entrada", style="green", width=8)
        table.add_column("Saída", style="red", width=8)
        table.add_column("Almoço", style="yellow", width=12)
        table.add_column("Horas", style="magenta", width=8)
        table.add_column("Saldo", style="white", width=8)
        
        total_horas_trabalhadas = 0
        total_dias_trabalhados = 0
        total_dias_uteis = 0
        
        dias_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB', 'DOM']
        
        # Iterar por todos os dias do mês até hoje
        data_atual = primeiro_dia_mes
        while data_atual <= hoje:
            data_str = data_atual.strftime("%Y-%m-%d")
            data_formatada = data_atual.strftime("%d/%m")
            dia_semana = dias_semana[data_atual.weekday()]
            
            # Considerar apenas dias úteis (segunda a sexta) para cálculo de dias úteis
            if data_atual.weekday() < 5:  # 0-4 = segunda a sexta
                total_dias_uteis += 1
            
            registros_dia = self._get_registros_ponto_por_data(data_str)
            calculo = self._calcular_horas_trabalhadas(registros_dia)
            
            # Formatação dos dados
            entrada = calculo['entrada'] or '-'
            saida = calculo['saida'] or '-'
            
            almoco = '-'
            if calculo['inicio_almoco'] and calculo['fim_almoco']:
                almoco = f"{calculo['inicio_almoco']}-{calculo['fim_almoco']}"
            elif calculo['inicio_almoco']:
                almoco = f"{calculo['inicio_almoco']}-?"
            
            horas_str = f"{calculo['horas_trabalhadas']:.1f}h" if calculo['horas_trabalhadas'] > 0 else '-'
            
            # Calcular saldo (horas extras ou faltantes)
            saldo = 0
            saldo_str = '-'
            if calculo['horas_trabalhadas'] > 0:
                saldo = calculo['horas_trabalhadas'] - carga_horaria_diaria
                if saldo > 0:
                    saldo_str = f"+{saldo:.1f}h"
                elif saldo < 0:
                    saldo_str = f"{saldo:.1f}h"
                else:
                    saldo_str = "0h"
                
                total_horas_trabalhadas += calculo['horas_trabalhadas']
                total_dias_trabalhados += 1
            
            # Colorir linha baseado no dia da semana e status
            if data_atual.weekday() >= 5:  # Fim de semana
                style = "dim blue"
            elif calculo['status'] == 'sem_registros':
                style = "red dim"
            elif calculo['status'] == 'incompleto':
                style = "yellow"
            else:
                style = "white"
            
            table.add_row(
                data_formatada,
                dia_semana,
                entrada,
                saida,
                almoco,
                horas_str,
                saldo_str,
                style=style
            )
            
            data_atual += timedelta(days=1)
        
        console.print(table)
        
        # Resumo do mês
        horas_esperadas_total = total_dias_uteis * carga_horaria_diaria
        saldo_total = total_horas_trabalhadas - (total_dias_trabalhados * carga_horaria_diaria)
        
        resumo_table = Table(title="Resumo do Mês", box=box.ROUNDED)
        resumo_table.add_column("Métrica", style="cyan")
        resumo_table.add_column("Valor", style="white")
        
        resumo_table.add_row("Dias úteis no período", str(total_dias_uteis))
        resumo_table.add_row("Dias trabalhados", str(total_dias_trabalhados))
        resumo_table.add_row("Total de horas trabalhadas", f"{total_horas_trabalhadas:.1f}h")
        resumo_table.add_row("Horas esperadas (dias trabalhados)", f"{total_dias_trabalhados * carga_horaria_diaria:.1f}h")
        resumo_table.add_row("Horas esperadas (dias úteis)", f"{horas_esperadas_total:.1f}h")
        
        if saldo_total > 0:
            resumo_table.add_row("Saldo (baseado em dias trabalhados)", f"[green]+{saldo_total:.1f}h (extras)[/green]")
        elif saldo_total < 0:
            resumo_table.add_row("Saldo (baseado em dias trabalhados)", f"[red]{saldo_total:.1f}h (faltantes)[/red]")
        else:
            resumo_table.add_row("Saldo (baseado em dias trabalhados)", "0h (em dia)")
        
        # Saldo considerando todos os dias úteis
        saldo_total_uteis = total_horas_trabalhadas - horas_esperadas_total
        if saldo_total_uteis > 0:
            resumo_table.add_row("Saldo (baseado em dias úteis)", f"[green]+{saldo_total_uteis:.1f}h (extras)[/green]")
        elif saldo_total_uteis < 0:
            resumo_table.add_row("Saldo (baseado em dias úteis)", f"[red]{saldo_total_uteis:.1f}h (faltantes)[/red]")
        else:
            resumo_table.add_row("Saldo (baseado em dias úteis)", "0h (em dia)")
        
        console.print()
        console.print(resumo_table)
        
        # Estatísticas adicionais
        if total_dias_trabalhados > 0:
            media_horas_dia = total_horas_trabalhadas / total_dias_trabalhados
            
            stats_table = Table(title="Estatísticas Adicionais", box=box.ROUNDED)
            stats_table.add_column("Métrica", style="cyan")
            stats_table.add_column("Valor", style="white")
            
            stats_table.add_row("Média de horas por dia trabalhado", f"{media_horas_dia:.1f}h")
            stats_table.add_row("Percentual de frequência", f"{(total_dias_trabalhados / total_dias_uteis * 100):.1f}%")
            
            console.print()
            console.print(stats_table)
        
        console.input("\nPressione Enter para continuar...")
    
    def _configuracoes_ponto(self):
        """Configurações do controle de ponto"""
        console.clear()
        self._display_header()
        console.print(Panel("⚙️ CONFIGURAÇÕES DO PONTO", style="cyan"))
        
        config = self.get_configuracoes_ponto()
        
        console.print(f"\n[bold]Configurações Atuais:[/bold]")
        console.print(f"Carga horária diária: {config.get('carga_horaria_diaria', 8)} horas")
        console.print(f"Horário de almoço: {config.get('horario_almoco', '12:00-13:00')}")
        
        console.input("\nPressione Enter para continuar...")
    
    def _notas_menu(self):
        """Menu de notas"""
        while True:
            console.clear()
            self._display_header()
            console.print(Panel("📝 NOTAS E LEMBRETES", style="green"))
            
            # Exibe últimas notas
            notas = self._get_notas()
            if notas:
                console.print("\n[bold]Últimas notas:[/bold]")
                for i, nota in enumerate(notas[:3], 1):
                    data_nota = nota.get('data', nota.get('created_at', 'N/A'))
                    console.print(f"{i}. {nota['titulo']} - {data_nota}")
            else:
                console.print("\n[yellow]Nenhuma nota encontrada[/yellow]")
            
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Opção", style="cyan", width=8)
            table.add_column("Ação", style="white")
            
            table.add_row("1", "✏️ Nova Nota")
            table.add_row("2", "📋 Listar Notas")
            table.add_row("3", "🔍 Buscar Nota")
            table.add_row("4", "🗑️ Excluir Nota")
            table.add_row("0", "🔙 Voltar")
            
            console.print(table)
            console.print()
            
            choice = Prompt.ask("Escolha uma opção", default="1")
            
            if choice == "1":
                self._nova_nota()
            elif choice == "2":
                self._listar_notas()
            elif choice == "3":
                self._buscar_nota()
            elif choice == "4":
                self._excluir_nota_menu()
            elif choice == "0":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _nova_nota(self):
        """Criar nova nota"""
        console.clear()
        self._display_header()
        console.print(Panel("✏️ NOVA NOTA", style="green"))
        
        titulo = Prompt.ask("Título da nota")
        if not titulo:
            return
        
        console.print("\nConteúdo da nota (pressione Enter duas vezes para finalizar):")
        conteudo_lines = []
        while True:
            line = input()
            if line == "" and conteudo_lines and conteudo_lines[-1] == "":
                break
            conteudo_lines.append(line)
        
        conteudo = "\n".join(conteudo_lines).strip()
        
        nota = {
            "titulo": titulo,
            "conteudo": conteudo,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "created_at": datetime.now(),
            "tags": []
        }
        
        self._salvar_nota(nota)
        
        console.print(f"\n[green]✅ Nota '{titulo}' criada com sucesso![/green]")
        console.input("\nPressione Enter para continuar...")
    
    def _listar_notas(self):
        """Listar todas as notas"""
        console.clear()
        self._display_header()
        console.print(Panel("📋 TODAS AS NOTAS", style="green"))
        
        notas = self._get_notas()
        if not notas:
            console.print("\n[yellow]Nenhuma nota encontrada.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Título", style="white")
        table.add_column("Data", style="dim")
        
        for nota in notas:
            nota_id = str(nota.get('_id', nota.get('id', 'N/A')))
            data_nota = nota.get('data', nota.get('created_at', 'N/A'))
            table.add_row(
                nota_id,
                nota["titulo"],
                str(data_nota)
            )
        
        console.print(table)
        console.input("\nPressione Enter para continuar...")
    
    def _buscar_nota(self):
        """Buscar nota por termo"""
        termo = Prompt.ask("Digite o termo de busca")
        if not termo:
            return
        
        resultados = []
        notas = self._get_notas()
        for nota in notas:
            if (termo.lower() in nota["titulo"].lower() or 
                termo.lower() in nota["conteudo"].lower()):
                resultados.append(nota)
        
        console.clear()
        self._display_header()
        console.print(Panel(f"🔍 RESULTADOS PARA '{termo}'", style="green"))
        
        if not resultados:
            console.print("\n[yellow]Nenhuma nota encontrada.[/yellow]")
        else:
            for nota in resultados:
                console.print(f"\n[bold]{nota['titulo']}[/bold] - {nota['data']}")
                console.print(f"{nota['conteudo'][:100]}...")
        
        console.input("\nPressione Enter para continuar...")
    
    def _excluir_nota_menu(self):
        """Menu para excluir nota"""
        notas = self._get_notas()
        if not notas:
            console.print("\n[yellow]Nenhuma nota para excluir.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        self._listar_notas()
        
        nota_id = Prompt.ask("ID da nota para excluir (0 para cancelar)")
        if nota_id == "0":
            return
        
        # Encontra a nota
        nota_encontrada = None
        for nota in notas:
            if str(nota.get('_id', nota.get('id', ''))) == nota_id:
                nota_encontrada = nota
                break
        
        if nota_encontrada:
            if Confirm.ask(f"Confirma exclusão da nota '{nota_encontrada['titulo']}'?"):
                if self._excluir_nota(nota_id):
                    console.print(f"\n[green]✅ Nota excluída com sucesso![/green]")
                else:
                    console.print(f"\n[red]Erro ao excluir nota.[/red]")
        else:
            console.print(f"\n[red]Nota com ID {nota_id} não encontrada.[/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _projetos_menu(self):
        """Menu de projetos"""
        console.clear()
        self._display_header()
        console.print(Panel("📁 PROJETOS", style="blue"))
        console.print("\n[dim italic]Funcionalidade em desenvolvimento...[/dim italic]")
        console.input("\nPressione Enter para continuar...")
    
    def _metas_menu(self):
        """Menu de metas"""
        console.clear()
        self._display_header()
        console.print(Panel("🎯 METAS", style="magenta"))
        console.print("\n[dim italic]Funcionalidade em desenvolvimento...[/dim italic]")
        console.input("\nPressione Enter para continuar...")
    
    def _dashboard(self):
        """Dashboard geral"""
        console.clear()
        self._display_header()
        console.print(Panel("📊 DASHBOARD ENCORA", style="yellow"))
        
        # Estatísticas básicas
        notas = self._get_notas()
        total_notas = len(notas)
        total_registros_ponto = len(self._get_todos_registros_ponto())
        
        # Registros de hoje
        hoje = datetime.now().strftime("%Y-%m-%d")
        registros_hoje = len(self._get_registros_ponto_por_data(hoje))
        
        stats_table = Table(title="Estatísticas", box=box.ROUNDED)
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", style="white")
        
        stats_table.add_row("Total de Notas", str(total_notas))
        stats_table.add_row("Registros de Ponto (Total)", str(total_registros_ponto))
        stats_table.add_row("Registros de Hoje", str(registros_hoje))
        
        console.print(stats_table)
        console.input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    app = EncoraModule()
    app.run()