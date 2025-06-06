import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json


@dataclass
class TodoistTask:
    id: str
    content: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = 0
    priority: int = 1  # 1-4 (4=highest)
    due: Optional[Dict[str, Any]] = None
    labels: List[str] = field(default_factory=list)
    is_completed: bool = False
    created_at: Optional[str] = None
    assignee_id: Optional[str] = None
    comment_count: int = 0
    url: Optional[str] = None


@dataclass
class TodoistProject:
    id: str
    name: str
    color: str
    parent_id: Optional[str] = None
    order: int = 0
    comment_count: int = 0
    is_shared: bool = False
    is_favorite: bool = False
    is_inbox_project: bool = False
    is_team_inbox: bool = False
    url: str = ""
    view_style: str = "list"


@dataclass
class TodoistLabel:
    id: str
    name: str
    color: str
    order: int = 0
    is_favorite: bool = False


@dataclass
class TodoistSection:
    id: str
    project_id: str
    order: int
    name: str


class TodoistClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Any]:
        """Make HTTP request to Todoist API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 204:  # No content
                return True
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    # Projects
    def get_projects(self) -> List[TodoistProject]:
        """Get all projects"""
        data = self._make_request("GET", "projects")
        if data:
            projects = []
            for project_data in data:
                # Filter only valid fields
                valid_fields = {'id', 'name', 'color', 'parent_id', 'order', 'comment_count',
                               'is_shared', 'is_favorite', 'is_inbox_project', 'is_team_inbox',
                               'url', 'view_style'}
                filtered_data = {k: v for k, v in project_data.items() if k in valid_fields}
                projects.append(TodoistProject(**filtered_data))
            return projects
        return []
    
    def get_project(self, project_id: str) -> Optional[TodoistProject]:
        """Get specific project"""
        data = self._make_request("GET", f"projects/{project_id}")
        if data:
            valid_fields = {'id', 'name', 'color', 'parent_id', 'order', 'comment_count',
                           'is_shared', 'is_favorite', 'is_inbox_project', 'is_team_inbox',
                           'url', 'view_style'}
            filtered_data = {k: v for k, v in data.items() if k in valid_fields}
            return TodoistProject(**filtered_data)
        return None
    
    def create_project(self, name: str, parent_id: Optional[str] = None, 
                      color: str = "grey", is_favorite: bool = False) -> Optional[TodoistProject]:
        """Create new project"""
        data = {
            "name": name,
            "color": color,
            "is_favorite": is_favorite
        }
        if parent_id:
            data["parent_id"] = parent_id
        
        result = self._make_request("POST", "projects", data)
        if result:
            valid_fields = {'id', 'name', 'color', 'parent_id', 'order', 'comment_count',
                           'is_shared', 'is_favorite', 'is_inbox_project', 'is_team_inbox',
                           'url', 'view_style'}
            filtered_data = {k: v for k, v in result.items() if k in valid_fields}
            return TodoistProject(**filtered_data)
        return None
    
    def update_project(self, project_id: str, name: Optional[str] = None, 
                      color: Optional[str] = None, is_favorite: Optional[bool] = None) -> bool:
        """Update project"""
        data = {}
        if name is not None:
            data["name"] = name
        if color is not None:
            data["color"] = color
        if is_favorite is not None:
            data["is_favorite"] = is_favorite
        
        return self._make_request("POST", f"projects/{project_id}", data) is not None
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        return self._make_request("DELETE", f"projects/{project_id}") is not None
    
    # Tasks
    def get_tasks(self, project_id: Optional[str] = None, section_id: Optional[str] = None,
                  label: Optional[str] = None, filter: Optional[str] = None) -> List[TodoistTask]:
        """Get active tasks"""
        params = {}
        if project_id:
            params["project_id"] = project_id
        if section_id:
            params["section_id"] = section_id
        if label:
            params["label"] = label
        if filter:
            params["filter"] = filter
        
        data = self._make_request("GET", "tasks", params)
        if data:
            tasks = []
            for task_data in data:
                # Filter only valid fields
                valid_fields = {'id', 'content', 'description', 'project_id', 'section_id',
                               'parent_id', 'order', 'priority', 'due', 'labels',
                               'is_completed', 'created_at', 'assignee_id', 'comment_count', 'url'}
                filtered_data = {k: v for k, v in task_data.items() if k in valid_fields}
                tasks.append(TodoistTask(**filtered_data))
            return tasks
        return []
    
    def get_task(self, task_id: str) -> Optional[TodoistTask]:
        """Get specific task"""
        data = self._make_request("GET", f"tasks/{task_id}")
        if data:
            valid_fields = {'id', 'content', 'description', 'project_id', 'section_id',
                           'parent_id', 'order', 'priority', 'due', 'labels',
                           'is_completed', 'created_at', 'assignee_id', 'comment_count', 'url'}
            filtered_data = {k: v for k, v in data.items() if k in valid_fields}
            return TodoistTask(**filtered_data)
        return None
    
    def create_task(self, content: str, description: Optional[str] = None,
                   project_id: Optional[str] = None, section_id: Optional[str] = None,
                   parent_id: Optional[str] = None, labels: Optional[List[str]] = None,
                   priority: int = 1, due_string: Optional[str] = None,
                   due_date: Optional[str] = None, due_lang: str = "pt") -> Optional[TodoistTask]:
        """Create new task"""
        data = {
            "content": content,
            "priority": priority
        }
        
        if description:
            data["description"] = description
        if project_id:
            data["project_id"] = project_id
        if section_id:
            data["section_id"] = section_id
        if parent_id:
            data["parent_id"] = parent_id
        if labels:
            data["labels"] = labels
        
        # Handle due date
        if due_string:
            data["due_string"] = due_string
            data["due_lang"] = due_lang
        elif due_date:
            data["due_date"] = due_date
        
        result = self._make_request("POST", "tasks", data)
        if result:
            valid_fields = {'id', 'content', 'description', 'project_id', 'section_id',
                           'parent_id', 'order', 'priority', 'due', 'labels',
                           'is_completed', 'created_at', 'assignee_id', 'comment_count', 'url'}
            filtered_data = {k: v for k, v in result.items() if k in valid_fields}
            return TodoistTask(**filtered_data)
        return None
    
    def update_task(self, task_id: str, content: Optional[str] = None,
                   description: Optional[str] = None, labels: Optional[List[str]] = None,
                   priority: Optional[int] = None, due_string: Optional[str] = None,
                   due_date: Optional[str] = None) -> bool:
        """Update task"""
        data = {}
        if content is not None:
            data["content"] = content
        if description is not None:
            data["description"] = description
        if labels is not None:
            data["labels"] = labels
        if priority is not None:
            data["priority"] = priority
        if due_string is not None:
            data["due_string"] = due_string
        if due_date is not None:
            data["due_date"] = due_date
        
        return self._make_request("POST", f"tasks/{task_id}", data) is not None
    
    def complete_task(self, task_id: str) -> bool:
        """Complete task"""
        return self._make_request("POST", f"tasks/{task_id}/close") is not None
    
    def reopen_task(self, task_id: str) -> bool:
        """Reopen task"""
        return self._make_request("POST", f"tasks/{task_id}/reopen") is not None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        return self._make_request("DELETE", f"tasks/{task_id}") is not None
    
    # Labels
    def get_labels(self) -> List[TodoistLabel]:
        """Get all labels"""
        data = self._make_request("GET", "labels")
        if data:
            labels = []
            for label_data in data:
                valid_fields = {'id', 'name', 'color', 'order', 'is_favorite'}
                filtered_data = {k: v for k, v in label_data.items() if k in valid_fields}
                labels.append(TodoistLabel(**filtered_data))
            return labels
        return []
    
    def create_label(self, name: str, color: str = "grey") -> Optional[TodoistLabel]:
        """Create new label"""
        data = {"name": name, "color": color}
        result = self._make_request("POST", "labels", data)
        if result:
            valid_fields = {'id', 'name', 'color', 'order', 'is_favorite'}
            filtered_data = {k: v for k, v in result.items() if k in valid_fields}
            return TodoistLabel(**filtered_data)
        return None
    
    def update_label(self, label_id: str, name: Optional[str] = None,
                    color: Optional[str] = None) -> bool:
        """Update label"""
        data = {}
        if name is not None:
            data["name"] = name
        if color is not None:
            data["color"] = color
        
        return self._make_request("POST", f"labels/{label_id}", data) is not None
    
    def delete_label(self, label_id: str) -> bool:
        """Delete label"""
        return self._make_request("DELETE", f"labels/{label_id}") is not None
    
    # Sections
    def get_sections(self, project_id: Optional[str] = None) -> List[TodoistSection]:
        """Get all sections"""
        params = {}
        if project_id:
            params["project_id"] = project_id
        
        data = self._make_request("GET", "sections", params)
        if data:
            sections = []
            for section_data in data:
                valid_fields = {'id', 'project_id', 'order', 'name'}
                filtered_data = {k: v for k, v in section_data.items() if k in valid_fields}
                sections.append(TodoistSection(**filtered_data))
            return sections
        return []
    
    def create_section(self, name: str, project_id: str, order: int = 0) -> Optional[TodoistSection]:
        """Create new section"""
        data = {
            "name": name,
            "project_id": project_id,
            "order": order
        }
        result = self._make_request("POST", "sections", data)
        if result:
            valid_fields = {'id', 'project_id', 'order', 'name'}
            filtered_data = {k: v for k, v in result.items() if k in valid_fields}
            return TodoistSection(**filtered_data)
        return None
    
    def update_section(self, section_id: str, name: str) -> bool:
        """Update section"""
        return self._make_request("POST", f"sections/{section_id}", {"name": name}) is not None
    
    def delete_section(self, section_id: str) -> bool:
        """Delete section"""
        return self._make_request("DELETE", f"sections/{section_id}") is not None
    
    # Comments
    def get_comments(self, task_id: str) -> List[Dict[str, Any]]:
        """Get comments for a task"""
        data = self._make_request("GET", "comments", {"task_id": task_id})
        return data if data else []
    
    def create_comment(self, task_id: str, content: str) -> Optional[Dict[str, Any]]:
        """Create comment on task"""
        data = {
            "task_id": task_id,
            "content": content
        }
        return self._make_request("POST", "comments", data)
    
    # Completed tasks
    def get_completed_tasks(self, project_id: Optional[str] = None, 
                           since: Optional[str] = None, until: Optional[str] = None,
                           limit: int = 30) -> List[Dict[str, Any]]:
        """Get completed tasks using Sync API"""
        # Use Sync API v9 for completed tasks
        sync_url = "https://api.todoist.com/sync/v9/completed/get_all"
        
        params = {"limit": limit}
        if project_id:
            params["project_id"] = project_id
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        
        try:
            response = requests.get(sync_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            if response.content:
                data = response.json()
                return data.get("items", []) if data else []
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar tarefas concluídas: {e}")
            return []