#!/usr/bin/env python3
"""
Test script to demonstrate the new standardized navigation system
"""

from utils.base_ui import BaseUI

class NavigationDemo(BaseUI):
    """Demo class to show standardized navigation"""
    
    def __init__(self):
        super().__init__()
    
    def demo_main_menu(self):
        """Demo main menu with standard navigation"""
        menu_options = [
            ("1", "🔢 Test Numbers"),
            ("2", "📝 Test Text"),
            ("3", "⚙️ Test Settings"),
            ("M", "🔙 Return to Main Menu")
        ]
        
        action_handlers = {
            "1": self.demo_numbers,
            "2": self.demo_text,
            "3": self.demo_settings
        }
        
        result = self.run_menu_loop(
            "📋 Navigation Demo - Submenu",
            menu_options,
            action_handlers
        )
        
        if result == "MAIN_MENU":
            self.show_info("Returned to main menu!")
        elif result == "BACK":
            self.show_info("Went back!")
    
    def demo_numbers(self):
        """Demo numbers functionality"""
        self.clear()
        header = self.create_header_panel("🔢 Numbers Demo")
        self.print(header)
        
        self.show_info("This is the numbers demo!")
        self.print("Try the standard navigation commands:")
        self.print("• Type [bold]0[/bold] to exit the system")
        self.print("• Type [bold]M[/bold] to return to main menu")
        self.print("• Type [bold]B[/bold] to go back to previous menu")
        
        self.wait_for_enter()
    
    def demo_text(self):
        """Demo text functionality"""
        self.clear()
        header = self.create_header_panel("📝 Text Demo")
        self.print(header)
        
        text = self.get_text_input("Enter some text (or try 0/M/B)")
        
        # Check for navigation commands
        nav_action = self.parse_navigation_input(text)
        if nav_action.value != "CONTINUE":
            self.show_info(f"Navigation command detected: {nav_action.value}")
            result = self.handle_navigation_action(nav_action)
            if result:
                return result
        else:
            self.show_success(f"You entered: {text}")
            self.wait_for_enter()
    
    def demo_settings(self):
        """Demo settings functionality"""
        self.clear()
        header = self.create_header_panel("⚙️ Settings Demo")
        self.print(header)
        
        self.show_info("Settings demo - standard navigation works here too!")
        
        # Demo a submenu within settings
        submenu_options = [
            ("1", "🎨 Theme Settings"),
            ("2", "🔔 Notification Settings"),
            ("B", "⬅️ Back to Previous Menu")
        ]
        
        submenu_handlers = {
            "1": lambda: self.show_success("Theme settings would go here!"),
            "2": lambda: self.show_success("Notification settings would go here!")
        }
        
        result = self.run_menu_loop(
            "⚙️ Settings Submenu",
            submenu_options,
            submenu_handlers
        )
        
        self.show_info(f"Settings submenu returned: {result}")
    
    def run_demo(self):
        """Run the navigation demo"""
        self.clear()
        welcome_header = self.create_header_panel(
            "🧪 Life OS Navigation Demo",
            "Demonstrating standardized navigation: 0=Exit, M=Main, B=Back"
        )
        self.print(welcome_header)
        
        self.print("\n[bold green]✨ Welcome to the Navigation Demo![/bold green]")
        self.print("\nThis demo shows the new standardized navigation system:")
        self.print("• [bold yellow]0[/bold yellow] = Exit system (works from anywhere)")
        self.print("• [bold yellow]M[/bold yellow] = Return to main menu (works from any submenu)")  
        self.print("• [bold yellow]B[/bold yellow] = Go back to previous menu")
        
        self.wait_for_enter("Press Enter to start the demo...")
        
        # Demo the submenu
        self.demo_main_menu()
        
        self.clear()
        goodbye_header = self.create_header_panel("👋 Demo Complete!")
        self.print(goodbye_header)
        self.show_success("Navigation demo completed successfully!")
        self.print("\nThe standardized navigation system is now active across Life OS!")

if __name__ == "__main__":
    demo = NavigationDemo()
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        demo.show_warning("Demo interrupted by user")