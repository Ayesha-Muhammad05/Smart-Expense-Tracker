# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 15:00:39 2025

@author: ayesh
"""
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 15:00:39 2025

@author: ayesh
"""
from expense import Expense
from ai import suggest_category

class ExpenseManager:
    def __init__(self):
        self.expenses = []  # List to store expenses
        self.next_id = 1  # Auto-increment ID

    def add_expense(self, description, amount, category, date):
        expense = Expense(self.next_id, description, amount, category, date)
        self.expenses.append(expense)
        self.next_id += 1
        return expense  # Return expense for confirmation

    def view_expenses(self):
        if not self.expenses:
            return "No expenses recorded."
        return "\n".join(str(expense) for expense in self.expenses)

    def delete_expense(self, expense_id):
        for expense in self.expenses:
            if expense.id == expense_id:
                self.expenses.remove(expense)
                return f"Expense ID {expense_id} deleted."
        return f"Expense ID {expense_id} not found."

    def edit_expense(self, expense_id, new_description=None, new_amount=None, new_category=None, new_date=None):
        for expense in self.expenses:
            if expense.id == expense_id:
                if new_description:
                    expense.description = new_description
                if new_amount is not None:
                    expense.amount = new_amount
                if new_category:
                    expense.category = new_category
                if new_date:
                    expense.date = new_date
                return f"Expense ID {expense_id} updated successfully."
        return f"Expense ID {expense_id} not found."

    def suggest_category(self, description):
        return suggest_category(description)

    def clear_all_expenses(self):
        self.expenses.clear()
        self.next_id = 1
        return "All expenses cleared."

# Example usage:
# manager = ExpenseManager()
# manager.add_expense("Lunch", 25, "Food", "2025-04-02")
# print(manager.view_expenses())
# print(manager.edit_expense(1, new_amount=30))
# print(manager.delete_expense(1))
# print(manager.suggest_category("pizza dinner"))
# print(manager.clear_all_expenses())
