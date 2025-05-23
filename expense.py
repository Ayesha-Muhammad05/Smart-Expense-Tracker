# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 15:42:27 2025

@author: ayesh
"""

#%% expense.py  # Expense-related classes
class Expense:
    def __init__(self, id, description, amount, category, date):
        self.id = id
        self.description = description
        self.amount = amount
        self.category = category
        self.date = date

    def __str__(self):
        return f"{self.date} | {self.category}: {self.description} - {self.amount} AED"

# Subclasses for specific expense types
class FoodExpense(Expense):
    def __init__(self, id, description, amount, date):
        super().__init__(id, description, amount, "Food", date)

class TransportExpense(Expense):
    def __init__(self, id, description, amount, date):
        super().__init__(id, description, amount, "Transport", date)

class EntertainmentExpense(Expense):
    def __init__(self, id, description, amount, date):
        super().__init__(id, description, amount, "Entertainment", date)
