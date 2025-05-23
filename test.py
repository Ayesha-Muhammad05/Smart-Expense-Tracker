# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 21:18:18 2025

@author: ayesh
"""

from expense_manager import ExpenseManager

manager = ExpenseManager()

# Add expenses
exp1 = manager.add_expense("Lunch", 50, "Food", "2025-04-01")
exp2 = manager.add_expense("Taxi", 30, "Transport", "2025-04-02")
print("\n--- All Expenses After Adding ---")
print(manager.view_expenses())

# Edit expense
print("\n--- Editing Expense 1 ---")
print(manager.edit_expense(exp1.id, new_description="Lunch at Cafe", new_amount=60))

# Delete expense
print("\n--- Deleting Expense 2 ---")
print(manager.delete_expense(exp2.id))

# View final expenses
print("\n--- Final Expenses ---")
print(manager.view_expenses())
