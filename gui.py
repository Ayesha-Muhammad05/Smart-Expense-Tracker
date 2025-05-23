
# gui.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Menu, CENTER, Toplevel
from tkinter import PhotoImage
import datetime
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os 

class SmartExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trackr – Expense Tracker")
        self.root.geometry("1000x750")
        self.expense_list = []
        self.chart_type = "pie"
        self.setup_database()
        self.build_layout()
        self.load_expenses_from_db()

    def setup_database(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "expenses.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                amount REAL,
                category TEXT,
                date TEXT
            )
        ''')
        self.conn.commit()

    def load_expenses_from_db(self):
        self.expense_list.clear()
        self.cursor.execute("SELECT id, description, amount, category, date FROM expenses")
        rows = self.cursor.fetchall()
        for row in rows:
            self.expense_list.append({
                'id': row[0],
                'description': row[1],
                'amount': row[2],
                'category': row[3],
                'date': row[4]
            })
        self.populate_expense_table()
        self.update_category_summary()
        self.render_chart_tab()
        self.update_savings_tab()

    def build_layout(self):
        self.notebook = ttk.Notebook(self.root)
        self.main_tab = ttk.Frame(self.notebook)
        self.chart_tab = ttk.Frame(self.notebook)
        self.savings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.chart_tab, text="Charts")
        self.notebook.add(self.savings_tab, text="Savings")
        self.notebook.pack(fill=BOTH, expand=True)

        self.build_main_tab()

    def build_main_tab(self):
        top_bar = ttk.Frame(self.main_tab)
        top_bar.pack(fill=X, padx=20, pady=(15, 5))
        ttk.Label(top_bar, text="📊", font=("Helvetica", 22)).pack(side=LEFT, padx=5)
        ttk.Label(top_bar, text="Trackr – Expense Tracker", font=("Helvetica", 20, "bold")).pack(side=LEFT)

        nav_frame = ttk.Frame(self.main_tab)
        nav_frame.pack(pady=10)
        ttk.Button(nav_frame, text="📈 Dashboard", bootstyle=PRIMARY, command=lambda: self.notebook.select(self.chart_tab)).grid(row=0, column=0, padx=15)
        ttk.Button(nav_frame, text="💰 Savings", bootstyle=SUCCESS, command=lambda: self.notebook.select(self.savings_tab)).grid(row=0, column=1, padx=15)

        search_frame = ttk.Frame(self.main_tab)
        search_frame.pack(pady=20)
        ttk.Label(search_frame, text="Search Category:", font=("Helvetica", 11)).grid(row=0, column=0, padx=10)
        self.search_entry = ttk.Combobox(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_search_suggestions)
        ttk.Button(search_frame, text="Search", bootstyle=WARNING, command=self.search_expenses).grid(row=0, column=2, padx=10)
        ttk.Button(search_frame, text="+ Add Expense", bootstyle=PRIMARY, width=20, command=self.open_add_expense_form).grid(row=0, column=3, padx=(30, 0))

        self.table_frame = ttk.Frame(self.main_tab)
        self.table_frame.pack(pady=10)
        self.populate_expense_table()

        summary_frame = ttk.Frame(self.main_tab)
        summary_frame.pack(pady=10)
        ttk.Label(summary_frame, text="View Total Expenses per Category:", font=("Helvetica", 12)).pack()
        self.category_summary = ttk.Combobox(summary_frame, values=[], width=45)
        self.category_summary.set("Select a category...")
        self.category_summary.pack(pady=5)
        self.category_summary.bind("<<ComboboxSelected>>", self.display_total_for_selected_category)

        self.total_label = ttk.Label(summary_frame, text="", font=("Helvetica", 11, "bold"))
        self.total_label.pack()

        bottom_frame = ttk.Frame(self.main_tab)
        bottom_frame.pack(pady=20)
        ttk.Button(bottom_frame, text="Export to CSV", bootstyle=SECONDARY, width=20, command=self.export_to_csv).pack(side=LEFT, padx=25)
        ttk.Button(bottom_frame, text="Clear All Expenses", bootstyle=DANGER, width=20, command=self.clear_all_expenses).pack(side=RIGHT, padx=25)

        ttk.Label(self.main_tab, text="“Stop chasing paper receipts.”", font=("Segoe UI", 12, "italic"), foreground="#00BFFF").pack(side=BOTTOM, pady=10)


    def update_savings_tab(self):
        for widget in self.savings_tab.winfo_children():
            widget.destroy()

        ttk.Label(self.savings_tab, text="Monthly Savings Tracker", font=("Helvetica", 16, "bold")).pack(pady=15)

        frame = ttk.Frame(self.savings_tab)
        frame.pack(pady=10)

        ttk.Label(frame, text="Monthly Income (AED):").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        income_entry = ttk.Entry(frame, width=30)
        income_entry.grid(row=0, column=1, pady=5)

        result_label = ttk.Label(self.savings_tab, text="", font=("Helvetica", 12))
        result_label.pack(pady=10)

        def calculate_savings():
            try:
                income = float(income_entry.get())
                total_expenses = sum(exp['amount'] for exp in self.expense_list)
                savings = income - total_expenses
                percentage = (savings / income) * 100 if income > 0 else 0
                
                if savings < 0:
                    result_label.config(
                        text=f"Income: {income:.2f} AED\nExpenses: {total_expenses:.2f} AED\nSavings: {savings:.2f} AED ({percentage:.1f}%)",
                        foreground="red"
                    )
                    messagebox.showwarning("Warning", "Your expenses exceed your income!")
                else:
                    result_label.config(
                        text=f"Income: {income:.2f} AED\nExpenses: {total_expenses:.2f} AED\nSavings: {savings:.2f} AED ({percentage:.1f}%)",
                        foreground="green"
                    )
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid income amount.")

        ttk.Button(self.savings_tab, text="Calculate Savings", bootstyle=SUCCESS, command=calculate_savings).pack(pady=5)
    def render_chart_tab(self):
        for widget in self.chart_tab.winfo_children():
            widget.destroy()

        control_frame = ttk.Frame(self.chart_tab)
        control_frame.pack(pady=10)
        ttk.Button(control_frame, text="Toggle Chart Type", command=self.toggle_chart_type).pack()

        self.cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = self.cursor.fetchall()
        if not data:
            ttk.Label(self.chart_tab, text="No data to display", font=("Helvetica", 14)).pack(pady=20)
            return

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=100)
        if self.chart_type == "pie":
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
            ax.set_title("Expense Distribution by Category")
            ax.axis('equal')
        else:
            ax.bar(categories, amounts, color='skyblue', edgecolor='black')
            ax.set_xlabel("Category")
            ax.set_ylabel("Total Amount")
            ax.set_title("Expense Bar Chart by Category")
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            ax.grid(axis='y', linestyle='--', alpha=0.7)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

    def toggle_chart_type(self):
        self.chart_type = "bar" if self.chart_type == "pie" else "pie"
        self.render_chart_tab()




    def update_search_suggestions(self, event):
        typed = self.search_entry.get().lower()
        self.cursor.execute("SELECT DISTINCT category FROM expenses WHERE LOWER(category) LIKE ?", (f"{typed}%",))
        matches = [row[0] for row in self.cursor.fetchall()]
        self.search_entry['values'] = matches
        if matches:
            self.search_entry.event_generate('<Down>')

    def update_category_summary(self):
        self.cursor.execute("SELECT DISTINCT category FROM expenses")
        categories = [row[0] for row in self.cursor.fetchall()]
        self.category_summary['values'] = categories

    def display_total_for_selected_category(self, event):
        selected_category = self.category_summary.get()
        self.cursor.execute("SELECT SUM(amount) FROM expenses WHERE category = ?", (selected_category,))
        total = self.cursor.fetchone()[0]
        if total:
            self.total_label.config(text=f"Total for {selected_category}: {total:.2f} AED")
        else:
            self.total_label.config(text="No expenses in this category.")

    def populate_expense_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.table_frame, text="Expense List", font=("Helvetica", 13, "bold")).pack(pady=10)

        headers = ttk.Frame(self.table_frame)
        headers.pack(fill=X, padx=250, pady=(5, 0))
        ttk.Label(headers, text="Description", width=20, font=("Helvetica", 10, "bold")).pack(side=LEFT)
        ttk.Label(headers, text="Category", width=15, font=("Helvetica", 10, "bold")).pack(side=LEFT)
        ttk.Label(headers, text="Amount", width=10, font=("Helvetica", 10, "bold")).pack(side=LEFT)
        ttk.Label(headers, text="Date", width=15, font=("Helvetica", 10, "bold")).pack(side=LEFT)

        for exp in self.expense_list:
            row = ttk.Frame(self.table_frame)
            row.pack(fill=X, padx=250, pady=6)

            ttk.Label(row, text=exp['description'], width=20).pack(side=LEFT)
            ttk.Label(row, text=exp['category'], width=15).pack(side=LEFT)
            ttk.Label(row, text=f"{exp['amount']} AED", width=10).pack(side=LEFT)
            ttk.Label(row, text=exp['date'], width=15).pack(side=LEFT)

            dot_button = ttk.Menubutton(row, text="⋮", bootstyle=SECONDARY, width=3)
            menu = Menu(dot_button, tearoff=0)
            menu.add_command(label="Edit", command=lambda eid=exp['id']: self.edit_expense(eid))
            menu.add_command(label="Delete", command=lambda eid=exp['id']: self.delete_expense(eid))
            dot_button['menu'] = menu
            dot_button.pack(side=RIGHT)

    def open_add_expense_form(self):
        form = Toplevel(self.root)
        form.title("Add New Expense")
        form.geometry("400x550")
        form.grab_set()

        ttk.Label(form, text="Description:*", anchor=CENTER).pack(pady=5)
        desc_entry = ttk.Entry(form, width=30)
        desc_entry.pack()

        ttk.Label(form, text="Amount (AED):*", anchor=CENTER).pack(pady=5)
        amount_entry = ttk.Entry(form, width=30)
        amount_entry.pack()

        ttk.Label(form, text="Category:*", anchor=CENTER).pack(pady=5)
        category_entry = ttk.Entry(form, width=30)
        category_entry.pack()

        ttk.Label(form, text="Date (YYYY-MM-DD):*", anchor=CENTER).pack(pady=5)
        date_entry = ttk.Entry(form, width=30)
        date_entry.pack()

        def auto_suggest_category(event):
            desc = desc_entry.get()
            suggested = self.suggest_category_from_description(desc)
            category_entry.delete(0, 'end')
            category_entry.insert(0, suggested)

        desc_entry.bind('<KeyRelease>', auto_suggest_category)

        def save_expense():
            try:
                desc = desc_entry.get().strip()
                amount = float(amount_entry.get())
                category = category_entry.get().strip()
                date = date_entry.get().strip()

                if desc and amount and category and date:
                    self.cursor.execute("INSERT INTO expenses (description, amount, category, date) VALUES (?, ?, ?, ?)",
                                        (desc, amount, category, date))
                    self.conn.commit()
                    self.load_expenses_from_db()
                    form.destroy()
                else:
                    messagebox.showwarning("Missing Info", "Please fill out all fields")
            except ValueError:
                messagebox.showerror("Invalid Input", "Amount must be a number")

        ttk.Button(form, text="Add Expense", bootstyle=SUCCESS, width=25, command=save_expense).pack(pady=25)

    def export_to_csv(self):
        import csv
        with open("expenses.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Description", "Amount", "Category", "Date"])
            for exp in self.expense_list:
                writer.writerow([exp['id'], exp['description'], exp['amount'], exp['category'], exp['date']])
        messagebox.showinfo("Exported", "Expenses exported to expenses.csv")

    def delete_expense(self, expense_id):
        self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        self.load_expenses_from_db()

    def edit_expense(self, expense_id):
        self.cursor.execute("SELECT description, amount, category, date FROM expenses WHERE id = ?", (expense_id,))
        exp = self.cursor.fetchone()
        if not exp:
            messagebox.showerror("Error", "Expense not found")
            return

        form = Toplevel(self.root)
        form.title("Edit Expense")
        form.geometry("400x550")
        form.grab_set()

        desc_entry = ttk.Entry(form, width=30)
        desc_entry.insert(0, exp[0])
        desc_entry.pack(pady=5)

        amount_entry = ttk.Entry(form, width=30)
        amount_entry.insert(0, str(exp[1]))
        amount_entry.pack(pady=5)

        category_entry = ttk.Entry(form, width=30)
        category_entry.insert(0, exp[2])
        category_entry.pack(pady=5)

        date_entry = ttk.Entry(form, width=30)
        date_entry.insert(0, exp[3])
        date_entry.pack(pady=5)

        def update():
            try:
                new_desc = desc_entry.get().strip()
                new_amount = float(amount_entry.get())
                new_category = category_entry.get().strip()
                new_date = date_entry.get().strip()

                if new_desc and new_amount and new_category and new_date:
                    self.cursor.execute("""
                        UPDATE expenses SET description = ?, amount = ?, category = ?, date = ?
                        WHERE id = ?
                    """, (new_desc, new_amount, new_category, new_date, expense_id))
                    self.conn.commit()
                    self.load_expenses_from_db()
                    form.destroy()
                else:
                    messagebox.showwarning("Missing Info", "All fields are required")
            except ValueError:
                messagebox.showerror("Invalid Input", "Amount must be a number")

        ttk.Button(form, text="Update Expense", bootstyle=SUCCESS, command=update).pack(pady=20)

    def clear_all_expenses(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete all expenses?")
        if confirm:
            self.cursor.execute("DELETE FROM expenses")
            self.conn.commit()
            self.load_expenses_from_db()

    def search_expenses(self):
        keyword = self.search_entry.get().lower().strip()
        if not keyword:
            self.load_expenses_from_db()
            return

        self.cursor.execute("SELECT id, description, amount, category, date FROM expenses WHERE LOWER(category) LIKE ?", (f"%{keyword}%",))
        rows = self.cursor.fetchall()

        self.expense_list = [{
            'id': row[0],
            'description': row[1],
            'amount': row[2],
            'category': row[3],
            'date': row[4]
        } for row in rows]

        self.populate_expense_table()
        
    def suggest_category_from_description(self, description):
        desc = description.lower()
        if any(word in desc for word in ["pizza", "burger", "snack", "coffee", "kfc"]):
            return "Food"
        elif any(word in desc for word in ["taxi", "uber", "bus", "fuel"]):
            return "Transport"
        elif any(word in desc for word in ["movie", "cinema", "netflix", "game"]):
            return "Entertainment"
        elif any(word in desc for word in ["med", "pharmacy", "hospital"]):
            return "Healthcare"
        else:
            return "Miscellaneous"


# Run the GUI
if __name__ == "__main__":
    from ttkbootstrap import Window
    root = Window(themename="pulse")
    app = SmartExpenseTrackerApp(root)
    root.mainloop()
