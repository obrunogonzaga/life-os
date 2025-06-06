#!/usr/bin/env python3
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from rich.layout import Layout
from rich import box
from typing import List, Optional, Dict
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.todoist_client import TodoistClient, TodoistTask, TodoistProject, TodoistLabel
from utils.config import Config

console = Console()


class TasksModule:
    def __init__(self):
        api_token = Config.TODOIST_API_TOKEN
        if not api_token:
            console.print("[red]❌ Token da API do Todoist não configurado![/red]")
            console.print("[yellow]Configure a variável TODOIST_API_TOKEN no arquivo .env[/yellow]")
            self.client = None
        else:
            self.client = TodoistClient(api_token)
    
    def run(self):
        """Menu principal do módulo de tarefas"""
        if not self.client:
            return
        
        while True:
            console.clear()
            self._display_header()
            
            options = [
                ("📝", "Tarefas", "Gerenciar tarefas"),
                ("📁", "Projetos", "Gerenciar projetos"),
                ("🏷️", "Etiquetas", "Gerenciar etiquetas"),
                ("📊", "Dashboard", "Visão geral e estatísticas"),
                ("🔍", "Buscar", "Buscar tarefas"),
                ("✅", "Concluídas", "Ver tarefas concluídas"),
                ("⚙️", "Configurações", "Configurações do módulo"),
                ("🔙", "Voltar", "Voltar ao menu principal")
            ]
            
            self._display_menu(options)
            
            choice = Prompt.ask("\n[cyan]Escolha uma opção[/cyan]", default="1")
            
            if choice == "1":
                self._tasks_menu()
            elif choice == "2":
                self._projects_menu()
            elif choice == "3":
                self._labels_menu()
            elif choice == "4":
                self._dashboard()
            elif choice == "5":
                self._search_tasks()
            elif choice == "6":
                self._completed_tasks()
            elif choice == "7":
                self._settings()
            elif choice == "8" or choice.upper() == "M":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _display_header(self):
        """Exibe cabeçalho do módulo"""
        header = Panel(
            Align.center(
                Text("✅ MÓDULO DE TAREFAS", style="bold cyan", justify="center")
            ),
            box=box.DOUBLE_EDGE,
            style="cyan"
        )
        console.print(header)
        console.print()
    
    def _display_menu(self, options: List[tuple]):
        """Exibe menu formatado"""
        table = Table(box=box.ROUNDED, show_header=False, expand=False)
        table.add_column("", style="cyan", width=3)
        table.add_column("Opção", style="white", width=20)
        table.add_column("Descrição", style="dim")
        
        for i, (icon, title, desc) in enumerate(options, 1):
            table.add_row(f"{i}", f"{icon} {title}", desc)
        
        console.print(Align.center(table))
    
    def _tasks_menu(self):
        """Menu de gerenciamento de tarefas"""
        while True:
            console.clear()
            self._display_header()
            console.print(Panel("📝 GERENCIAMENTO DE TAREFAS", style="cyan"))
            
            # Lista tarefas ativas
            tasks = self.client.get_tasks()
            if tasks:
                self._display_tasks(tasks)
            else:
                console.print("\n[yellow]Nenhuma tarefa encontrada.[/yellow]")
            
            console.print("\n[cyan]Opções:[/cyan]")
            console.print("1. ➕ Adicionar tarefa")
            console.print("2. ✏️  Editar tarefa")
            console.print("3. ✅ Marcar como concluída")
            console.print("4. 🗑️  Excluir tarefa")
            console.print("5. 🏷️  Gerenciar etiquetas da tarefa")
            console.print("6. 🔄 Atualizar lista")
            console.print("7. 📁 Filtrar por projeto")
            console.print("8. 🎯 Filtrar por prioridade")
            console.print("9. 📅 Tarefas de hoje")
            console.print("10. 📆 Próximos 7 dias")
            console.print("11. ⚠️  Tarefas atrasadas")
            console.print("12. 🔙 Voltar")
            
            choice = Prompt.ask("\n[cyan]Escolha uma opção[/cyan]", default="12")
            
            if choice == "1":
                self._add_task()
            elif choice == "2":
                self._edit_task(tasks)
            elif choice == "3":
                self._complete_task(tasks)
            elif choice == "4":
                self._delete_task(tasks)
            elif choice == "5":
                self._manage_task_labels(tasks)
            elif choice == "6":
                continue  # Atualiza a lista
            elif choice == "7":
                self._filter_by_project()
            elif choice == "8":
                self._filter_by_priority()
            elif choice == "9":
                self._show_tasks_today()
            elif choice == "10":
                self._show_tasks_next_7_days()
            elif choice == "11":
                self._show_overdue_tasks()
            elif choice == "12":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _display_tasks(self, tasks: List[TodoistTask], show_project: bool = True):
        """Exibe lista de tarefas"""
        table = Table(title="Tarefas Ativas", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Tarefa", style="white", no_wrap=False)
        if show_project:
            table.add_column("Projeto", style="blue")
        table.add_column("Prioridade", style="yellow", width=10)
        table.add_column("Prazo", style="magenta")
        table.add_column("Etiquetas", style="green")
        
        # Busca projetos para mostrar nomes
        projects = {p.id: p.name for p in self.client.get_projects()}
        
        priority_map = {1: "Baixa", 2: "Normal", 3: "Alta", 4: "Urgente"}
        priority_colors = {1: "white", 2: "yellow", 3: "orange3", 4: "red"}
        
        for i, task in enumerate(tasks, 1):
            project_name = projects.get(task.project_id, "Inbox") if task.project_id else "Inbox"
            priority_text = Text(priority_map[task.priority], style=priority_colors[task.priority])
            
            due_text = ""
            if task.due:
                if "date" in task.due:
                    due_date = datetime.fromisoformat(task.due["date"].replace("Z", "+00:00"))
                    due_text = due_date.strftime("%d/%m/%Y")
                elif "string" in task.due:
                    due_text = task.due["string"]
            
            labels_text = ", ".join(task.labels) if task.labels else ""
            
            row = [str(i), task.content]
            if show_project:
                row.append(project_name)
            row.extend([priority_text, due_text, labels_text])
            
            table.add_row(*row)
        
        console.print(table)
    
    def _add_task(self):
        """Adiciona nova tarefa"""
        console.clear()
        console.print(Panel("➕ ADICIONAR NOVA TAREFA", style="cyan"))
        
        # Conteúdo da tarefa
        content = Prompt.ask("\n[cyan]Título da tarefa[/cyan]")
        if not content:
            return
        
        # Descrição (opcional)
        description = Prompt.ask("[cyan]Descrição (opcional)[/cyan]", default="")
        
        # Projeto
        projects = self.client.get_projects()
        if projects:
            console.print("\n[cyan]Projetos disponíveis:[/cyan]")
            for i, project in enumerate(projects, 1):
                console.print(f"{i}. {project.name}")
            
            project_choice = IntPrompt.ask(
                "[cyan]Escolha o projeto (0 para Inbox)[/cyan]", 
                default=0
            )
            project_id = projects[project_choice - 1].id if 0 < project_choice <= len(projects) else None
        else:
            project_id = None
        
        # Prioridade
        console.print("\n[cyan]Prioridade:[/cyan]")
        console.print("1. Baixa")
        console.print("2. Normal")
        console.print("3. Alta")
        console.print("4. Urgente")
        priority = IntPrompt.ask("[cyan]Escolha a prioridade[/cyan]", default=2)
        
        # Data de vencimento
        due_string = Prompt.ask("\n[cyan]Prazo (ex: hoje, amanhã, sexta, 25 dez)[/cyan]", default="")
        
        # Etiquetas
        labels = self.client.get_labels()
        selected_labels = []
        if labels:
            console.print("\n[cyan]Etiquetas disponíveis:[/cyan]")
            for i, label in enumerate(labels, 1):
                console.print(f"{i}. {label.name}")
            
            label_choices = Prompt.ask(
                "[cyan]Escolha as etiquetas (números separados por vírgula)[/cyan]", 
                default=""
            )
            if label_choices:
                for choice in label_choices.split(","):
                    try:
                        idx = int(choice.strip()) - 1
                        if 0 <= idx < len(labels):
                            selected_labels.append(labels[idx].name)
                    except:
                        pass
        
        # Criar tarefa
        task = self.client.create_task(
            content=content,
            description=description if description else None,
            project_id=project_id,
            priority=priority,
            due_string=due_string if due_string else None,
            labels=selected_labels if selected_labels else None
        )
        
        if task:
            console.print(f"\n[green]✅ Tarefa '{content}' criada com sucesso![/green]")
        else:
            console.print(f"\n[red]❌ Erro ao criar tarefa![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _edit_task(self, tasks: List[TodoistTask]):
        """Edita uma tarefa existente"""
        if not tasks:
            console.print("[yellow]Nenhuma tarefa para editar.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        task_num = IntPrompt.ask("\n[cyan]Número da tarefa para editar[/cyan]")
        if 1 <= task_num <= len(tasks):
            task = tasks[task_num - 1]
            
            console.clear()
            console.print(Panel(f"✏️ EDITAR TAREFA: {task.content}", style="cyan"))
            
            # Novo conteúdo
            content = Prompt.ask(
                f"\n[cyan]Novo título (Enter para manter)[/cyan]", 
                default=task.content
            )
            
            # Nova descrição
            current_desc = task.description if task.description else "(sem descrição)"
            description = Prompt.ask(
                f"[cyan]Nova descrição (atual: {current_desc})[/cyan]", 
                default=task.description if task.description else ""
            )
            
            # Nova prioridade
            priority_map = {1: "Baixa", 2: "Normal", 3: "Alta", 4: "Urgente"}
            console.print(f"\n[cyan]Prioridade atual: {priority_map[task.priority]}[/cyan]")
            console.print("1. Baixa")
            console.print("2. Normal")
            console.print("3. Alta")
            console.print("4. Urgente")
            priority = IntPrompt.ask("[cyan]Nova prioridade[/cyan]", default=task.priority)
            
            # Novo prazo
            due_string = Prompt.ask(
                "\n[cyan]Novo prazo (deixe vazio para remover)[/cyan]", 
                default=""
            )
            
            # Atualizar tarefa
            success = self.client.update_task(
                task_id=task.id,
                content=content if content != task.content else None,
                description=description if description != task.description else None,
                priority=priority if priority != task.priority else None,
                due_string=due_string if due_string else None
            )
            
            if success:
                console.print(f"\n[green]✅ Tarefa atualizada com sucesso![/green]")
            else:
                console.print(f"\n[red]❌ Erro ao atualizar tarefa![/red]")
        else:
            console.print("[red]Número de tarefa inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _complete_task(self, tasks: List[TodoistTask]):
        """Marca tarefa como concluída"""
        if not tasks:
            console.print("[yellow]Nenhuma tarefa para concluir.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        task_num = IntPrompt.ask("\n[cyan]Número da tarefa para concluir[/cyan]")
        if 1 <= task_num <= len(tasks):
            task = tasks[task_num - 1]
            
            if Confirm.ask(f"\n[yellow]Concluir tarefa '{task.content}'?[/yellow]"):
                if self.client.complete_task(task.id):
                    console.print(f"\n[green]✅ Tarefa concluída![/green]")
                else:
                    console.print(f"\n[red]❌ Erro ao concluir tarefa![/red]")
        else:
            console.print("[red]Número de tarefa inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _delete_task(self, tasks: List[TodoistTask]):
        """Exclui uma tarefa"""
        if not tasks:
            console.print("[yellow]Nenhuma tarefa para excluir.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        task_num = IntPrompt.ask("\n[cyan]Número da tarefa para excluir[/cyan]")
        if 1 <= task_num <= len(tasks):
            task = tasks[task_num - 1]
            
            if Confirm.ask(f"\n[red]Excluir tarefa '{task.content}'?[/red]"):
                if self.client.delete_task(task.id):
                    console.print(f"\n[green]✅ Tarefa excluída![/green]")
                else:
                    console.print(f"\n[red]❌ Erro ao excluir tarefa![/red]")
        else:
            console.print("[red]Número de tarefa inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _manage_task_labels(self, tasks: List[TodoistTask]):
        """Gerencia etiquetas de uma tarefa"""
        if not tasks:
            console.print("[yellow]Nenhuma tarefa disponível.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        task_num = IntPrompt.ask("\n[cyan]Número da tarefa[/cyan]")
        if 1 <= task_num <= len(tasks):
            task = tasks[task_num - 1]
            
            console.clear()
            console.print(Panel(f"🏷️ GERENCIAR ETIQUETAS: {task.content}", style="cyan"))
            
            console.print(f"\n[cyan]Etiquetas atuais:[/cyan] {', '.join(task.labels) if task.labels else '(nenhuma)'}")
            
            labels = self.client.get_labels()
            if not labels:
                console.print("\n[yellow]Nenhuma etiqueta disponível.[/yellow]")
                console.input("\nPressione Enter para continuar...")
                return
            
            console.print("\n[cyan]Etiquetas disponíveis:[/cyan]")
            for i, label in enumerate(labels, 1):
                status = "✓" if label.name in (task.labels or []) else " "
                console.print(f"{i}. [{status}] {label.name}")
            
            label_choices = Prompt.ask(
                "\n[cyan]Escolha as etiquetas (números separados por vírgula)[/cyan]", 
                default=""
            )
            
            new_labels = []
            if label_choices:
                for choice in label_choices.split(","):
                    try:
                        idx = int(choice.strip()) - 1
                        if 0 <= idx < len(labels):
                            new_labels.append(labels[idx].name)
                    except:
                        pass
            
            if self.client.update_task(task_id=task.id, labels=new_labels):
                console.print(f"\n[green]✅ Etiquetas atualizadas![/green]")
            else:
                console.print(f"\n[red]❌ Erro ao atualizar etiquetas![/red]")
        else:
            console.print("[red]Número de tarefa inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _filter_by_project(self):
        """Filtra tarefas por projeto"""
        projects = self.client.get_projects()
        if not projects:
            console.print("[yellow]Nenhum projeto encontrado.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        console.clear()
        console.print(Panel("📁 FILTRAR POR PROJETO", style="cyan"))
        
        console.print("\n[cyan]Projetos disponíveis:[/cyan]")
        for i, project in enumerate(projects, 1):
            console.print(f"{i}. {project.name}")
        
        project_choice = IntPrompt.ask("\n[cyan]Escolha o projeto[/cyan]")
        if 1 <= project_choice <= len(projects):
            project = projects[project_choice - 1]
            tasks = self.client.get_tasks(project_id=project.id)
            
            console.clear()
            console.print(Panel(f"📁 TAREFAS DO PROJETO: {project.name}", style="cyan"))
            
            if tasks:
                self._display_tasks(tasks, show_project=False)
            else:
                console.print("\n[yellow]Nenhuma tarefa neste projeto.[/yellow]")
        else:
            console.print("[red]Projeto inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _filter_by_priority(self):
        """Filtra tarefas por prioridade"""
        console.clear()
        console.print(Panel("🎯 FILTRAR POR PRIORIDADE", style="cyan"))
        
        console.print("\n[cyan]Escolha a prioridade:[/cyan]")
        console.print("1. Baixa")
        console.print("2. Normal")
        console.print("3. Alta")
        console.print("4. Urgente")
        
        priority = IntPrompt.ask("\n[cyan]Prioridade[/cyan]")
        if 1 <= priority <= 4:
            all_tasks = self.client.get_tasks()
            tasks = [t for t in all_tasks if t.priority == priority]
            
            priority_map = {1: "BAIXA", 2: "NORMAL", 3: "ALTA", 4: "URGENTE"}
            console.clear()
            console.print(Panel(f"🎯 TAREFAS COM PRIORIDADE {priority_map[priority]}", style="cyan"))
            
            if tasks:
                self._display_tasks(tasks)
            else:
                console.print("\n[yellow]Nenhuma tarefa com esta prioridade.[/yellow]")
        else:
            console.print("[red]Prioridade inválida![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _show_tasks_today(self):
        """Mostra tarefas para hoje"""
        console.clear()
        console.print(Panel("📅 TAREFAS PARA HOJE", style="cyan"))
        
        tasks = self.client.get_tasks_today()
        
        if tasks:
            self._display_tasks(tasks)
        else:
            console.print("\n[yellow]Nenhuma tarefa para hoje.[/yellow]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _show_tasks_next_7_days(self):
        """Mostra tarefas dos próximos 7 dias"""
        console.clear()
        console.print(Panel("📆 TAREFAS DOS PRÓXIMOS 7 DIAS", style="cyan"))
        
        tasks = self.client.get_tasks_next_7_days()
        
        if tasks:
            # Organizar por data
            from datetime import datetime
            tasks_by_date = {}
            
            for task in tasks:
                if task.due and 'date' in task.due:
                    date_str = task.due['date']
                    try:
                        task_date = datetime.fromisoformat(date_str.replace('Z', '')).date()
                        date_key = task_date.strftime("%d/%m/%Y")
                        if date_key not in tasks_by_date:
                            tasks_by_date[date_key] = []
                        tasks_by_date[date_key].append(task)
                    except (ValueError, KeyError):
                        # Tarefas sem data válida
                        if "Sem data" not in tasks_by_date:
                            tasks_by_date["Sem data"] = []
                        tasks_by_date["Sem data"].append(task)
            
            # Exibir por data
            for date_str, date_tasks in sorted(tasks_by_date.items()):
                console.print(f"\n[bold cyan]{date_str}[/bold cyan]")
                self._display_tasks(date_tasks)
        else:
            console.print("\n[yellow]Nenhuma tarefa para os próximos 7 dias.[/yellow]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _show_overdue_tasks(self):
        """Mostra tarefas atrasadas"""
        console.clear()
        console.print(Panel("⚠️ TAREFAS ATRASADAS", style="red"))
        
        tasks = self.client.get_overdue_tasks()
        
        if tasks:
            self._display_tasks(tasks)
        else:
            console.print("\n[green]Nenhuma tarefa atrasada! 🎉[/green]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _projects_menu(self):
        """Menu de gerenciamento de projetos"""
        while True:
            console.clear()
            self._display_header()
            console.print(Panel("📁 GERENCIAMENTO DE PROJETOS", style="cyan"))
            
            # Lista projetos
            projects = self.client.get_projects()
            if projects:
                self._display_projects(projects)
            else:
                console.print("\n[yellow]Nenhum projeto encontrado.[/yellow]")
            
            console.print("\n[cyan]Opções:[/cyan]")
            console.print("1. ➕ Criar projeto")
            console.print("2. ✏️  Editar projeto")
            console.print("3. 🗑️  Excluir projeto")
            console.print("4. 📊 Ver estatísticas do projeto")
            console.print("5. 🔄 Atualizar lista")
            console.print("6. 🔙 Voltar")
            
            choice = Prompt.ask("\n[cyan]Escolha uma opção[/cyan]", default="6")
            
            if choice == "1":
                self._create_project()
            elif choice == "2":
                self._edit_project(projects)
            elif choice == "3":
                self._delete_project(projects)
            elif choice == "4":
                self._project_stats(projects)
            elif choice == "5":
                continue  # Atualiza a lista
            elif choice == "6":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _display_projects(self, projects: List[TodoistProject]):
        """Exibe lista de projetos"""
        table = Table(title="Projetos", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Nome", style="white")
        table.add_column("Cor", style="yellow")
        table.add_column("Favorito", style="green")
        table.add_column("Compartilhado", style="blue")
        
        for i, project in enumerate(projects, 1):
            fav = "⭐" if project.is_favorite else ""
            shared = "👥" if project.is_shared else ""
            table.add_row(
                str(i),
                project.name,
                project.color,
                fav,
                shared
            )
        
        console.print(table)
    
    def _create_project(self):
        """Cria novo projeto"""
        console.clear()
        console.print(Panel("➕ CRIAR NOVO PROJETO", style="cyan"))
        
        name = Prompt.ask("\n[cyan]Nome do projeto[/cyan]")
        if not name:
            return
        
        # Cores disponíveis no Todoist
        colors = [
            "berry_red", "red", "orange", "yellow", "olive_green",
            "lime_green", "green", "mint_green", "teal", "sky_blue",
            "light_blue", "blue", "grape", "violet", "lavender",
            "magenta", "salmon", "charcoal", "grey", "taupe"
        ]
        
        console.print("\n[cyan]Cores disponíveis:[/cyan]")
        for i, color in enumerate(colors, 1):
            console.print(f"{i}. {color}")
        
        color_choice = IntPrompt.ask("\n[cyan]Escolha a cor[/cyan]", default=13)
        color = colors[color_choice - 1] if 1 <= color_choice <= len(colors) else "grey"
        
        is_favorite = Confirm.ask("\n[cyan]Marcar como favorito?[/cyan]", default=False)
        
        project = self.client.create_project(
            name=name,
            color=color,
            is_favorite=is_favorite
        )
        
        if project:
            console.print(f"\n[green]✅ Projeto '{name}' criado com sucesso![/green]")
        else:
            console.print(f"\n[red]❌ Erro ao criar projeto![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _edit_project(self, projects: List[TodoistProject]):
        """Edita um projeto"""
        if not projects:
            console.print("[yellow]Nenhum projeto para editar.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        project_num = IntPrompt.ask("\n[cyan]Número do projeto para editar[/cyan]")
        if 1 <= project_num <= len(projects):
            project = projects[project_num - 1]
            
            console.clear()
            console.print(Panel(f"✏️ EDITAR PROJETO: {project.name}", style="cyan"))
            
            name = Prompt.ask(
                f"\n[cyan]Novo nome (Enter para manter)[/cyan]", 
                default=project.name
            )
            
            is_favorite = Confirm.ask(
                f"\n[cyan]Marcar como favorito?[/cyan]", 
                default=project.is_favorite
            )
            
            success = self.client.update_project(
                project_id=project.id,
                name=name if name != project.name else None,
                is_favorite=is_favorite if is_favorite != project.is_favorite else None
            )
            
            if success:
                console.print(f"\n[green]✅ Projeto atualizado com sucesso![/green]")
            else:
                console.print(f"\n[red]❌ Erro ao atualizar projeto![/red]")
        else:
            console.print("[red]Número de projeto inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _delete_project(self, projects: List[TodoistProject]):
        """Exclui um projeto"""
        if not projects:
            console.print("[yellow]Nenhum projeto para excluir.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        project_num = IntPrompt.ask("\n[cyan]Número do projeto para excluir[/cyan]")
        if 1 <= project_num <= len(projects):
            project = projects[project_num - 1]
            
            if project.is_inbox_project:
                console.print("\n[red]❌ Não é possível excluir o projeto Inbox![/red]")
            elif Confirm.ask(f"\n[red]Excluir projeto '{project.name}' e todas suas tarefas?[/red]"):
                if self.client.delete_project(project.id):
                    console.print(f"\n[green]✅ Projeto excluído![/green]")
                else:
                    console.print(f"\n[red]❌ Erro ao excluir projeto![/red]")
        else:
            console.print("[red]Número de projeto inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _project_stats(self, projects: List[TodoistProject]):
        """Mostra estatísticas de um projeto"""
        if not projects:
            console.print("[yellow]Nenhum projeto disponível.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        project_num = IntPrompt.ask("\n[cyan]Número do projeto[/cyan]")
        if 1 <= project_num <= len(projects):
            project = projects[project_num - 1]
            
            console.clear()
            console.print(Panel(f"📊 ESTATÍSTICAS: {project.name}", style="cyan"))
            
            # Tarefas do projeto
            tasks = self.client.get_tasks(project_id=project.id)
            
            # Estatísticas
            total_tasks = len(tasks)
            by_priority = {1: 0, 2: 0, 3: 0, 4: 0}
            overdue = 0
            today = 0
            
            for task in tasks:
                by_priority[task.priority] += 1
                
                if task.due and "date" in task.due:
                    due_date = datetime.fromisoformat(task.due["date"].replace("Z", "+00:00"))
                    now = datetime.now(due_date.tzinfo)
                    
                    if due_date.date() < now.date():
                        overdue += 1
                    elif due_date.date() == now.date():
                        today += 1
            
            # Exibir estatísticas
            stats_table = Table(box=box.ROUNDED, show_header=False)
            stats_table.add_column("Métrica", style="cyan")
            stats_table.add_column("Valor", style="white")
            
            stats_table.add_row("Total de tarefas", str(total_tasks))
            stats_table.add_row("Tarefas atrasadas", f"[red]{overdue}[/red]" if overdue > 0 else "0")
            stats_table.add_row("Tarefas para hoje", f"[yellow]{today}[/yellow]")
            stats_table.add_row("", "")
            stats_table.add_row("Por prioridade:", "")
            stats_table.add_row("  • Urgente", f"[red]{by_priority[4]}[/red]")
            stats_table.add_row("  • Alta", f"[orange3]{by_priority[3]}[/orange3]")
            stats_table.add_row("  • Normal", f"[yellow]{by_priority[2]}[/yellow]")
            stats_table.add_row("  • Baixa", f"[white]{by_priority[1]}[/white]")
            
            console.print(stats_table)
            
            # Tarefas concluídas recentemente
            completed = self.client.get_completed_tasks(project_id=project.id, limit=5)
            if completed:
                console.print("\n[cyan]Últimas tarefas concluídas:[/cyan]")
                for task in completed[:5]:
                    console.print(f"  ✓ {task.get('content', 'Sem título')}")
        else:
            console.print("[red]Número de projeto inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _labels_menu(self):
        """Menu de gerenciamento de etiquetas"""
        while True:
            console.clear()
            self._display_header()
            console.print(Panel("🏷️ GERENCIAMENTO DE ETIQUETAS", style="cyan"))
            
            # Lista etiquetas
            labels = self.client.get_labels()
            if labels:
                self._display_labels(labels)
            else:
                console.print("\n[yellow]Nenhuma etiqueta encontrada.[/yellow]")
            
            console.print("\n[cyan]Opções:[/cyan]")
            console.print("1. ➕ Criar etiqueta")
            console.print("2. ✏️  Editar etiqueta")
            console.print("3. 🗑️  Excluir etiqueta")
            console.print("4. 📋 Ver tarefas com etiqueta")
            console.print("5. 🔄 Atualizar lista")
            console.print("6. 🔙 Voltar")
            
            choice = Prompt.ask("\n[cyan]Escolha uma opção[/cyan]", default="6")
            
            if choice == "1":
                self._create_label()
            elif choice == "2":
                self._edit_label(labels)
            elif choice == "3":
                self._delete_label(labels)
            elif choice == "4":
                self._view_label_tasks(labels)
            elif choice == "5":
                continue  # Atualiza a lista
            elif choice == "6":
                break
            else:
                console.print("[red]Opção inválida![/red]")
                console.input("\nPressione Enter para continuar...")
    
    def _display_labels(self, labels: List[TodoistLabel]):
        """Exibe lista de etiquetas"""
        table = Table(title="Etiquetas", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Nome", style="white")
        table.add_column("Cor", style="yellow")
        table.add_column("Favorita", style="green")
        
        for i, label in enumerate(labels, 1):
            fav = "⭐" if label.is_favorite else ""
            table.add_row(
                str(i),
                label.name,
                label.color,
                fav
            )
        
        console.print(table)
    
    def _create_label(self):
        """Cria nova etiqueta"""
        console.clear()
        console.print(Panel("➕ CRIAR NOVA ETIQUETA", style="cyan"))
        
        name = Prompt.ask("\n[cyan]Nome da etiqueta[/cyan]")
        if not name:
            return
        
        # Cores disponíveis no Todoist
        colors = [
            "berry_red", "red", "orange", "yellow", "olive_green",
            "lime_green", "green", "mint_green", "teal", "sky_blue",
            "light_blue", "blue", "grape", "violet", "lavender",
            "magenta", "salmon", "charcoal", "grey", "taupe"
        ]
        
        console.print("\n[cyan]Cores disponíveis:[/cyan]")
        for i, color in enumerate(colors, 1):
            console.print(f"{i}. {color}")
        
        color_choice = IntPrompt.ask("\n[cyan]Escolha a cor[/cyan]", default=13)
        color = colors[color_choice - 1] if 1 <= color_choice <= len(colors) else "grey"
        
        label = self.client.create_label(name=name, color=color)
        
        if label:
            console.print(f"\n[green]✅ Etiqueta '{name}' criada com sucesso![/green]")
        else:
            console.print(f"\n[red]❌ Erro ao criar etiqueta![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _edit_label(self, labels: List[TodoistLabel]):
        """Edita uma etiqueta"""
        if not labels:
            console.print("[yellow]Nenhuma etiqueta para editar.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        label_num = IntPrompt.ask("\n[cyan]Número da etiqueta para editar[/cyan]")
        if 1 <= label_num <= len(labels):
            label = labels[label_num - 1]
            
            console.clear()
            console.print(Panel(f"✏️ EDITAR ETIQUETA: {label.name}", style="cyan"))
            
            name = Prompt.ask(
                f"\n[cyan]Novo nome (Enter para manter)[/cyan]", 
                default=label.name
            )
            
            success = self.client.update_label(
                label_id=label.id,
                name=name if name != label.name else None
            )
            
            if success:
                console.print(f"\n[green]✅ Etiqueta atualizada com sucesso![/green]")
            else:
                console.print(f"\n[red]❌ Erro ao atualizar etiqueta![/red]")
        else:
            console.print("[red]Número de etiqueta inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _delete_label(self, labels: List[TodoistLabel]):
        """Exclui uma etiqueta"""
        if not labels:
            console.print("[yellow]Nenhuma etiqueta para excluir.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        label_num = IntPrompt.ask("\n[cyan]Número da etiqueta para excluir[/cyan]")
        if 1 <= label_num <= len(labels):
            label = labels[label_num - 1]
            
            if Confirm.ask(f"\n[red]Excluir etiqueta '{label.name}'?[/red]"):
                if self.client.delete_label(label.id):
                    console.print(f"\n[green]✅ Etiqueta excluída![/green]")
                else:
                    console.print(f"\n[red]❌ Erro ao excluir etiqueta![/red]")
        else:
            console.print("[red]Número de etiqueta inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _view_label_tasks(self, labels: List[TodoistLabel]):
        """Visualiza tarefas com uma etiqueta específica"""
        if not labels:
            console.print("[yellow]Nenhuma etiqueta disponível.[/yellow]")
            console.input("\nPressione Enter para continuar...")
            return
        
        label_num = IntPrompt.ask("\n[cyan]Número da etiqueta[/cyan]")
        if 1 <= label_num <= len(labels):
            label = labels[label_num - 1]
            
            console.clear()
            console.print(Panel(f"📋 TAREFAS COM ETIQUETA: {label.name}", style="cyan"))
            
            tasks = self.client.get_tasks(label=label.name)
            if tasks:
                self._display_tasks(tasks)
            else:
                console.print("\n[yellow]Nenhuma tarefa com esta etiqueta.[/yellow]")
        else:
            console.print("[red]Número de etiqueta inválido![/red]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _dashboard(self):
        """Dashboard com visão geral"""
        console.clear()
        self._display_header()
        console.print(Panel("📊 DASHBOARD", style="cyan"))
        
        # Buscar dados
        tasks = self.client.get_tasks()
        projects = self.client.get_projects()
        labels = self.client.get_labels()
        
        # Estatísticas gerais
        total_tasks = len(tasks)
        overdue = 0
        today = 0
        upcoming = 0
        no_date = 0
        
        by_priority = {1: 0, 2: 0, 3: 0, 4: 0}
        by_project = {}
        
        for task in tasks:
            by_priority[task.priority] += 1
            
            # Por projeto
            project_name = next((p.name for p in projects if p.id == task.project_id), "Inbox")
            by_project[project_name] = by_project.get(project_name, 0) + 1
            
            # Por data
            if task.due and "date" in task.due:
                due_date = datetime.fromisoformat(task.due["date"].replace("Z", "+00:00"))
                now = datetime.now(due_date.tzinfo)
                
                if due_date.date() < now.date():
                    overdue += 1
                elif due_date.date() == now.date():
                    today += 1
                elif due_date.date() <= (now + timedelta(days=7)).date():
                    upcoming += 1
            else:
                no_date += 1
        
        # Layout do dashboard
        layout = Layout()
        layout.split_column(
            Layout(name="stats", size=8),
            Layout(name="projects", size=10),
            Layout(name="priority", size=8)
        )
        
        # Estatísticas gerais
        stats_table = Table(box=box.ROUNDED, title="📈 Estatísticas Gerais")
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", style="white")
        
        stats_table.add_row("Total de tarefas", str(total_tasks))
        stats_table.add_row("Tarefas atrasadas", f"[red]{overdue}[/red]" if overdue > 0 else "0")
        stats_table.add_row("Tarefas para hoje", f"[yellow]{today}[/yellow]")
        stats_table.add_row("Próximos 7 dias", str(upcoming))
        stats_table.add_row("Sem data", str(no_date))
        stats_table.add_row("Total de projetos", str(len(projects)))
        stats_table.add_row("Total de etiquetas", str(len(labels)))
        
        layout["stats"].update(stats_table)
        
        # Por projeto
        project_table = Table(box=box.ROUNDED, title="📁 Tarefas por Projeto")
        project_table.add_column("Projeto", style="cyan")
        project_table.add_column("Tarefas", style="white")
        project_table.add_column("Gráfico", style="green")
        
        max_tasks = max(by_project.values()) if by_project else 1
        for project, count in sorted(by_project.items(), key=lambda x: x[1], reverse=True):
            bar_length = int((count / max_tasks) * 20)
            bar = "█" * bar_length
            project_table.add_row(project, str(count), bar)
        
        layout["projects"].update(project_table)
        
        # Por prioridade
        priority_table = Table(box=box.ROUNDED, title="🎯 Tarefas por Prioridade")
        priority_table.add_column("Prioridade", style="cyan")
        priority_table.add_column("Tarefas", style="white")
        priority_table.add_column("Porcentagem", style="yellow")
        
        priority_names = {1: "Baixa", 2: "Normal", 3: "Alta", 4: "Urgente"}
        priority_colors = {1: "white", 2: "yellow", 3: "orange3", 4: "red"}
        
        for priority in [4, 3, 2, 1]:  # Do mais urgente para o menos
            count = by_priority[priority]
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            priority_table.add_row(
                Text(priority_names[priority], style=priority_colors[priority]),
                str(count),
                f"{percentage:.1f}%"
            )
        
        layout["priority"].update(priority_table)
        
        console.print(layout)
        
        console.input("\nPressione Enter para continuar...")
    
    def _search_tasks(self):
        """Busca tarefas"""
        console.clear()
        console.print(Panel("🔍 BUSCAR TAREFAS", style="cyan"))
        
        search_term = Prompt.ask("\n[cyan]Digite o termo de busca[/cyan]")
        if not search_term:
            return
        
        all_tasks = self.client.get_tasks()
        found_tasks = []
        
        search_lower = search_term.lower()
        for task in all_tasks:
            if (search_lower in task.content.lower() or 
                (task.description and search_lower in task.description.lower()) or
                any(search_lower in label.lower() for label in (task.labels or []))):
                found_tasks.append(task)
        
        console.clear()
        console.print(Panel(f"🔍 RESULTADOS PARA: {search_term}", style="cyan"))
        
        if found_tasks:
            self._display_tasks(found_tasks)
            console.print(f"\n[green]Encontradas {len(found_tasks)} tarefas[/green]")
        else:
            console.print("\n[yellow]Nenhuma tarefa encontrada.[/yellow]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _completed_tasks(self):
        """Visualiza tarefas concluídas"""
        console.clear()
        console.print(Panel("✅ TAREFAS CONCLUÍDAS", style="cyan"))
        
        # Opções de período
        console.print("\n[cyan]Período:[/cyan]")
        console.print("1. Hoje")
        console.print("2. Últimos 7 dias")
        console.print("3. Últimos 30 dias")
        console.print("4. Todos")
        
        period_choice = IntPrompt.ask("\n[cyan]Escolha o período[/cyan]", default=2)
        
        # Calcular datas
        now = datetime.now()
        since = None
        
        if period_choice == 1:
            since = now.replace(hour=0, minute=0, second=0).isoformat()
        elif period_choice == 2:
            since = (now - timedelta(days=7)).isoformat()
        elif period_choice == 3:
            since = (now - timedelta(days=30)).isoformat()
        
        completed = self.client.get_completed_tasks(since=since, limit=50)
        
        if completed:
            table = Table(title="Tarefas Concluídas", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=3)
            table.add_column("Tarefa", style="white", no_wrap=False)
            table.add_column("Projeto", style="blue")
            table.add_column("Concluída em", style="green")
            
            projects = {p.id: p.name for p in self.client.get_projects()}
            
            for i, task in enumerate(completed, 1):
                project_name = projects.get(task.get("project_id"), "Inbox")
                completed_at = task.get("completed_at", "")
                if completed_at:
                    try:
                        dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        completed_at = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                
                table.add_row(
                    str(i),
                    task.get("content", "Sem título"),
                    project_name,
                    completed_at
                )
            
            console.print(table)
            console.print(f"\n[green]Total: {len(completed)} tarefas concluídas[/green]")
        else:
            console.print("\n[yellow]Nenhuma tarefa concluída no período.[/yellow]")
        
        console.input("\nPressione Enter para continuar...")
    
    def _settings(self):
        """Configurações do módulo"""
        console.clear()
        console.print(Panel("⚙️ CONFIGURAÇÕES", style="cyan"))
        
        console.print("\n[cyan]Informações da conta:[/cyan]")
        console.print(f"Token API: {'*' * 20}...{(Config.TODOIST_API_TOKEN or '')[-4:]}")
        
        console.print("\n[cyan]Estatísticas de uso:[/cyan]")
        try:
            tasks = self.client.get_tasks()
            projects = self.client.get_projects()
            labels = self.client.get_labels()
            
            console.print(f"Total de tarefas ativas: {len(tasks)}")
            console.print(f"Total de projetos: {len(projects)}")
            console.print(f"Total de etiquetas: {len(labels)}")
        except:
            console.print("[red]Erro ao obter estatísticas[/red]")
        
        console.print("\n[cyan]Opções:[/cyan]")
        console.print("1. 🔄 Testar conexão com API")
        console.print("2. 📥 Exportar dados")
        console.print("3. 🔙 Voltar")
        
        choice = Prompt.ask("\n[cyan]Escolha uma opção[/cyan]", default="3")
        
        if choice == "1":
            console.print("\n[yellow]Testando conexão...[/yellow]")
            try:
                projects = self.client.get_projects()
                console.print(f"[green]✅ Conexão OK! {len(projects)} projetos encontrados.[/green]")
            except Exception as e:
                console.print(f"[red]❌ Erro na conexão: {e}[/red]")
        elif choice == "2":
            self._export_data()
        
        if choice != "3":
            console.input("\nPressione Enter para continuar...")
    
    def _export_data(self):
        """Exporta dados para arquivo"""
        console.print("\n[cyan]Exportando dados...[/cyan]")
        
        try:
            import json
            from datetime import datetime
            
            # Coletar dados
            data = {
                "exported_at": datetime.now().isoformat(),
                "tasks": [task.__dict__ for task in self.client.get_tasks()],
                "projects": [project.__dict__ for project in self.client.get_projects()],
                "labels": [label.__dict__ for label in self.client.get_labels()],
                "completed_tasks": self.client.get_completed_tasks(limit=100)
            }
            
            # Salvar arquivo
            filename = f"todoist_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("data", filename)
            
            os.makedirs("data", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            console.print(f"\n[green]✅ Dados exportados para: {filepath}[/green]")
        except Exception as e:
            console.print(f"\n[red]❌ Erro ao exportar: {e}[/red]")


def main():
    """Função principal para testar o módulo"""
    module = TasksModule()
    module.run()


if __name__ == "__main__":
    main()