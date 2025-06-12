#!/usr/bin/env python3
"""
Test script to verify finance module navigation
"""

from modules.finances import FinancesModule

print("🧪 Testing Finance Module Navigation")
print("=" * 50)
print("\nTry the following commands:")
print("• 0 - Exit system (from any menu)")
print("• M or m - Return to main menu")
print("• B or b - Go back to previous menu")
print("\nStarting finance module...\n")

# Run the finance module
try:
    finance_app = FinancesModule()
    finance_app.run()
except KeyboardInterrupt:
    print("\n\nTest interrupted")
except SystemExit:
    print("\n\nSystem exited successfully!")