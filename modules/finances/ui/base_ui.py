"""
Base UI Components for Finance Module

This module provides common UI utilities and Rich components that are shared
across all finance module interfaces. It implements reusable patterns for
tables, forms, menus, and user interactions.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from typing import List, Dict, Optional, Any, Union
from enum import Enum


class BaseUI:
    """Base class for all finance module UI components"""
    
    def __init__(self):
        self.console = Console()
    
    # ===============================
    # BASIC OUTPUT METHODS
    # ===============================
    
    def clear(self):
        """Clear the console"""
        self.console.clear()
    
    def print(self, content, **kwargs):
        """Print content to console with optional formatting"""
        self.console.print(content, **kwargs)
    
    def print_newline(self):
        """Print a newline"""
        self.console.print()
    
    # ===============================
    # MESSAGE FORMATTING
    # ===============================
    
    def show_success(self, message: str):
        """Display a success message"""
        self.console.print(f"[green]✓ {message}[/green]")
    
    def show_error(self, message: str):
        """Display an error message"""
        self.console.print(f"[red]✗ Erro: {message}[/red]")
    
    def show_warning(self, message: str):
        """Display a warning message"""
        self.console.print(f"[yellow]⚠ {message}[/yellow]")
    
    def show_info(self, message: str):
        """Display an info message"""
        self.console.print(f"[blue]ℹ {message}[/blue]")
    
    # ===============================
    # PANEL CREATION
    # ===============================
    
    def create_header_panel(self, title: str, subtitle: str = "", style: str = "cyan") -> Panel:
        """Create a header panel with title and optional subtitle"""
        content = f"[bold {style}]{title}[/bold {style}]"
        if subtitle:
            content += f"\n[dim]{subtitle}[/dim]"
        
        return Panel(
            Align.center(content),
            style=style
        )
    
    def create_info_panel(self, content: str, title: str = "", style: str = "blue") -> Panel:
        """Create an information panel"""
        return Panel(
            content,
            title=title if title else None,
            style=style
        )
    
    def create_panel(self, content: str, title: str = "", style: str = "white") -> Panel:
        """Create a general panel"""
        return Panel(
            content,
            title=title if title else None,
            style=style
        )
    
    # ===============================
    # TABLE CREATION
    # ===============================
    
    def create_menu_table(self, items: List[tuple], show_header: bool = False) -> Table:
        """
        Create a menu table with options and descriptions
        
        Args:
            items: List of (option, description) tuples
            show_header: Whether to show table header
        """
        table = Table(show_header=show_header, box=None, padding=(0, 2))
        table.add_column("Opção", style="bold yellow", width=4)
        table.add_column("Descrição", style="white")
        
        for option, description in items:
            table.add_row(option, description)
        
        return table
    
    def create_data_table(self, columns: List[tuple], data: List[List[str]], 
                         title: str = "") -> Table:
        """
        Create a data table with specified columns and data
        
        Args:
            columns: List of (column_name, style, width) tuples
            data: List of row data
            title: Optional table title
        """
        table = Table(title=title if title else None, show_header=True, header_style="bold cyan")
        
        # Add columns
        for col_name, style, width in columns:
            if width:
                table.add_column(col_name, style=style, width=width)
            else:
                table.add_column(col_name, style=style)
        
        # Add data rows
        for row in data:
            table.add_row(*row)
        
        return table
    
    def create_table(self, title: str = "", columns: List[str] = None) -> Table:
        """
        Create a simple table with optional title and columns
        
        Args:
            title: Optional table title
            columns: List of column names
        """
        table = Table(title=title if title else None, show_header=True, header_style="bold cyan")
        
        if columns:
            for col in columns:
                table.add_column(col)
        
        return table
    
    # ===============================
    # USER INPUT METHODS
    # ===============================
    
    def get_menu_choice(self, prompt_text: str, choices: List[str], 
                       default: Optional[str] = None) -> str:
        """Get a menu choice from user with validation"""
        return Prompt.ask(prompt_text, choices=choices, default=default)
    
    def get_text_input(self, prompt_text: str, default: str = "") -> str:
        """Get text input from user"""
        result = Prompt.ask(prompt_text, default=default if default else "")
        return result.strip()
    
    def get_int_input(self, prompt_text: str, default: Optional[int] = None,
                     min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """Get integer input from user with validation"""
        while True:
            try:
                if default is not None:
                    result = IntPrompt.ask(prompt_text, default=default)
                else:
                    result = IntPrompt.ask(prompt_text)
                
                if min_value is not None and result < min_value:
                    self.show_error(f"Valor deve ser maior ou igual a {min_value}")
                    continue
                
                if max_value is not None and result > max_value:
                    self.show_error(f"Valor deve ser menor ou igual a {max_value}")
                    continue
                
                return result
            except Exception as e:
                self.show_error(f"Valor inválido: {e}")
    
    def get_float_input(self, prompt_text: str, default: Optional[float] = None,
                       min_value: Optional[float] = None) -> float:
        """Get float input from user with validation"""
        while True:
            try:
                if default is not None:
                    result = FloatPrompt.ask(prompt_text, default=default)
                else:
                    result = FloatPrompt.ask(prompt_text)
                
                if min_value is not None and result < min_value:
                    self.show_error(f"Valor deve ser maior ou igual a {min_value}")
                    continue
                
                return result
            except Exception as e:
                self.show_error(f"Valor inválido: {e}")
    
    def get_confirmation(self, prompt_text: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user"""
        return Confirm.ask(prompt_text, default=default)
    
    def get_enum_choice(self, prompt_text: str, enum_class: Enum, 
                       display_func: Optional[callable] = None) -> Any:
        """
        Get user choice from an enum
        
        Args:
            prompt_text: Text to display to user
            enum_class: Enum class to choose from
            display_func: Optional function to format enum values for display
        """
        options = list(enum_class)
        
        self.print(f"\n[bold]{prompt_text}[/bold]")
        for i, option in enumerate(options, 1):
            display_text = display_func(option) if display_func else option.value
            self.print(f"[yellow]{i}[/yellow]. {display_text}")
        
        choice_idx = self.get_int_input("Escolha uma opção", min_value=1, max_value=len(options))
        return options[choice_idx - 1]
    
    # ===============================
    # SELECTION HELPERS
    # ===============================
    
    def select_from_list(self, items: List[Any], title: str, 
                        display_func: callable, id_func: callable = None,
                        allow_none: bool = False) -> Optional[Any]:
        """
        Allow user to select an item from a list
        
        Args:
            items: List of items to choose from
            title: Title to display
            display_func: Function to format item for display
            id_func: Function to get item ID (for display)
            allow_none: Whether to allow "none" selection
        """
        if not items:
            self.show_warning("Nenhum item disponível para seleção")
            return None
        
        self.print(f"\n[bold cyan]{title}[/bold cyan]")
        
        for i, item in enumerate(items, 1):
            id_text = f" (ID: {id_func(item)[:8]}...)" if id_func else ""
            self.print(f"[yellow]{i}[/yellow]. {display_func(item)}{id_text}")
        
        if allow_none:
            self.print(f"[yellow]0[/yellow]. Nenhum")
        
        max_choice = len(items)
        min_choice = 0 if allow_none else 1
        
        choice = self.get_int_input("Escolha uma opção", min_value=min_choice, max_value=max_choice)
        
        if choice == 0 and allow_none:
            return None
        
        return items[choice - 1]
    
    # ===============================
    # FORMATTING HELPERS
    # ===============================
    
    def format_currency(self, value: float) -> str:
        """Format a currency value"""
        return f"R$ {value:,.2f}"
    
    def format_percentage(self, value: float) -> str:
        """Format a percentage value"""
        return f"{value:.1f}%"
    
    def format_id(self, id_str: str, length: int = 8) -> str:
        """Format an ID for display (truncated)"""
        return f"{id_str[:length]}..." if len(id_str) > length else id_str
    
    def format_boolean_icon(self, value: bool, true_icon: str = "🟢", 
                           false_icon: str = "🔴") -> str:
        """Format a boolean value as an icon"""
        return true_icon if value else false_icon
    
    def format_status_icon(self, status: bool) -> str:
        """Format a status as check/X icon"""
        return "✓" if status else "✗"
    
    def format_date(self, date_str: str, format_length: int = 10) -> str:
        """Format a date string for display"""
        return date_str[:format_length] if date_str else "N/A"
    
    # ===============================
    # NAVIGATION HELPERS
    # ===============================
    
    def wait_for_enter(self, message: str = "Pressione Enter para continuar..."):
        """Wait for user to press Enter"""
        Prompt.ask(f"\n[dim]{message}[/dim]", default="")
    
    def show_back_option(self):
        """Show the back to menu option"""
        self.print("\n[dim]Digite 'M' para voltar ao menu principal[/dim]")
    
    # ===============================
    # LAYOUT HELPERS
    # ===============================
    
    def create_dashboard_layout(self) -> Layout:
        """Create a dashboard-style layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        return layout
    
    def create_two_column_layout(self) -> Layout:
        """Create a two-column layout"""
        layout = Layout()
        layout.split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        return layout
    
    # ===============================
    # ERROR HANDLING
    # ===============================
    
    def handle_exception(self, e: Exception, context: str = ""):
        """Handle and display an exception"""
        error_msg = f"Erro{' em ' + context if context else ''}: {str(e)}"
        self.show_error(error_msg)
    
    def safe_execute(self, func: callable, error_context: str = "", 
                    return_on_error: Any = None) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func()
        except Exception as e:
            self.handle_exception(e, error_context)
            return return_on_error