"""
Created on Tue Apr  1 15:32:28 2025

@author: ayesh
"""

import os
os.chdir("C:/Users/ayesh/OneDrive - Emirates Aviation University/Assignments-Spring25/SmartExpenseTracker")

import sqlite3
import os
import matplotlib.pyplot as plt
import csv
from expense import Expense  # Importing the Expense class

class ExpenseDatabase:
    def __init__(self):
        # Set up the database folder and path
        self.db_folder = os.path.join(os.getcwd(), "database")
        self.db_path = os.path.join(self.db_folder, "expenses.db")
        os.makedirs(self.db_folder, exist_ok=True)

        # Connect to SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Create Expenses table (with category ID reference)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        self.conn.commit()

    # Add a new category if it doesn’t exist
    def add_category(self, category_name):
        try:
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Ignore if category already exists

    # Get all categories
    def get_categories(self):
        self.cursor.execute("SELECT * FROM categories")
        return self.cursor.fetchall()

    # Get category ID from name
    def get_category_id(self, category_name):
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Add an expense with a category ID, preventing duplicates
    def add_expense(self, expense):
        try:
            # Check if the expense already exists
            self.cursor.execute(
                "SELECT id FROM expenses WHERE description = ? AND amount = ? AND category_id = ? AND date = ?",
                (expense.description, expense.amount, self.get_category_id(expense.category), expense.date)
            )
            if self.cursor.fetchone():
                print("Expense already exists. Skipping duplicate entry.")
                return

            # Get category ID, and if it doesn't exist, add it
            category_id = self.get_category_id(expense.category)
            if category_id is None:
                self.add_category(expense.category)
                category_id = self.get_category_id(expense.category)

            # Insert the expense with the category ID
            self.cursor.execute(
                "INSERT INTO expenses (description, amount, category_id, date) VALUES (?, ?, ?, ?)",
                (expense.description, expense.amount, category_id, expense.date)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding expense: {e}")

    # Retrieve expenses with category names
    def get_expenses(self):
        self.cursor.execute('''
            SELECT e.id, e.description, e.amount, c.name, e.date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
        ''')
        rows = self.cursor.fetchall()
        return [Expense(row[0], row[1], row[2], row[3], row[4]) for row in rows]

    # Retrieve total expenses per category
    def get_total_expenses_per_category(self):
        self.cursor.execute('''
            SELECT c.name, SUM(e.amount) 
            FROM expenses e 
            JOIN categories c ON e.category_id = c.id 
            GROUP BY c.name
        ''')
        return self.cursor.fetchall()

    # Delete an expense by ID
    def delete_expense(self, expense_id):
        try:
            self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting expense: {e}")

    # Clear all expenses
    def clear_all_expenses(self):
        try:
            self.cursor.execute("DELETE FROM expenses")
            self.conn.commit()
            print("All expenses cleared successfully.")
        except sqlite3.Error as e:
            print(f"Error clearing expenses: {e}")

    # Generate and display refined charts for expenses
    def visualize_expenses(self):
        data = self.get_total_expenses_per_category()
        if not data:
            print("No expenses to display.")
            return

        categories, amounts = zip(*data)

        # Define colors
        colors = plt.cm.Paired.colors[:len(categories)]

        # Pie Chart
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor': 'black'})
        plt.title("Expense Distribution")

        # Bar Chart
        plt.subplot(1, 2, 2)
        plt.bar(categories, amounts, color=colors, edgecolor='black')
        plt.xlabel("Categories")
        plt.ylabel("Total Amount")
        plt.title("Total Expenses per Category")
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Show charts
        plt.tight_layout()
        plt.show()

    # Export expenses to CSV
    def export_to_csv(self, filename="expenses.csv"):
        expenses = self.get_expenses()
        if not expenses:
            print("No expenses to export.")
            return

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Description", "Amount", "Category", "Date"])
            for exp in expenses:
                writer.writerow([exp.id, exp.description, exp.amount, exp.category, exp.date])

        print(f"Expenses exported successfully to {filename}!")

    # Close the database connection
    def close(self):
        self.conn.close()

# Run setup if executed directly
if __name__ == "__main__":
    db = ExpenseDatabase()
    print("Database setup complete!")

    # Ensure correct number of arguments when creating an Expense object
    test_expense = Expense(None, "Test Expense", 100.0, "Miscellaneous", "2025-04-03")
    db.add_expense(test_expense)
    print("Test expense added!")

    # Fetch and display expenses
    expenses = db.get_expenses()
    print("\nAll Expenses:")
    for exp in expenses:
        print(f"- {exp.description} | {exp.amount} | {exp.category} | {exp.date}")

    # Fetch and display total expenses per category
    print("\nTotal Expenses per Category:")
    totals = db.get_total_expenses_per_category()
    for category, total in totals:
        print(f"- {category}: {total}")

    # Visualize expenses
    db.visualize_expenses()

    # Export expenses
    db.export_to_csv()

    # Cleanup
    db.close()
