import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk

# Create the main application window
app = tk.Tk()
app.title("Expense Manager")

def add_money_source():
    # Create a new window for adding a money source
    add_money_source_window = tk.Toplevel(app)
    add_money_source_window.title("Add Money Source")

    # Labels and Entry widgets for user input
    tk.Label(add_money_source_window, text="Name:").pack()
    name_entry = tk.Entry(add_money_source_window)
    name_entry.pack()

    tk.Label(add_money_source_window, text="Initial Amount (default = 0):").pack()
    initial_amount_entry = tk.Entry(add_money_source_window)
    initial_amount_entry.pack()

    tk.Label(add_money_source_window, text="Description (default = NA):").pack()
    description_entry = tk.Entry(add_money_source_window)
    description_entry.pack()

    def save_money_source():
        name = name_entry.get()
        initial_amount = float(initial_amount_entry.get()) if initial_amount_entry.get() else 0.0
        description = description_entry.get() if description_entry.get() else "NA"

        # Insert data into the money_sources table
        conn = sqlite3.connect('expense_manager.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO money_sources (name, amount, description) VALUES (?, ?, ?)",
                       (name, initial_amount, description))
        conn.commit()
        conn.close()

        # Display success message
        messagebox.showinfo("Success", "Money source added successfully")

        # Close the add money source window
        add_money_source_window.destroy()
        display_money_sources()

    # Button to save the money source
    save_button = tk.Button(add_money_source_window, text="Save", command=save_money_source)
    save_button.pack()


def add_transaction():
    # Create a new window for adding a transaction
    add_transaction_window = tk.Toplevel(app)
    add_transaction_window.title("Add Transaction")

    # Labels and Entry/Dropdown widgets for user input
    tk.Label(add_transaction_window, text="Amount:").pack()
    amount_entry = tk.Entry(add_transaction_window)
    amount_entry.pack()

    # Retrieve money source names for dropdown
    conn = sqlite3.connect('expense_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM money_sources")
    money_source_names = [row[0] for row in cursor.fetchall()]
    conn.close()

    tk.Label(add_transaction_window, text="Money Source:").pack()
    money_source_var = tk.StringVar(add_transaction_window)
    money_source_var.set("Select Money Source")
    money_source_dropdown = tk.OptionMenu(add_transaction_window, money_source_var, *money_source_names)
    money_source_dropdown.pack()

    tk.Label(add_transaction_window, text="Type:").pack()
    transaction_type_var = tk.StringVar(add_transaction_window)
    transaction_type_var.set("Select Type")
    transaction_type_dropdown = tk.OptionMenu(add_transaction_window, transaction_type_var, "Add Money", "Deduct Money")
    transaction_type_dropdown.pack()

    tk.Label(add_transaction_window, text="Description:").pack()
    description_entry = tk.Entry(add_transaction_window)
    description_entry.pack()

    def save_transaction():
        amount = float(amount_entry.get())
        money_source = money_source_var.get()
        transaction_type = transaction_type_var.get()
        description = description_entry.get()

        # Retrieve the current balance of the selected money source
        conn = sqlite3.connect('expense_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount FROM money_sources WHERE name=?", (money_source,))
        money_source_id, money_before = cursor.fetchone()

        # Update money_sources table with new balance
        new_money_after = money_before + amount if transaction_type == "Add Money" else money_before - amount
        cursor.execute("UPDATE money_sources SET amount=? WHERE id=?", (new_money_after, money_source_id))
        conn.commit()

        # Insert data into transactions table
        cursor.execute("INSERT INTO transactions (amount, money_source_id, description, type, money_before, money_after) VALUES (?, ?, ?, ?, ?, ?)",
                       (amount, money_source_id, description, transaction_type.lower(), money_before, new_money_after))
        conn.commit()
        conn.close()

        # Display success message
        messagebox.showinfo("Success", "Transaction added successfully")

        # Close the add transaction window
        add_transaction_window.destroy()
        display_money_sources()

    # Button to save the transaction
    save_button = tk.Button(add_transaction_window, text="Save", command=save_transaction)
    save_button.pack()


def show_transactions(money_source_id):
    transactions_window = tk.Toplevel(app)
    transactions_window.title("Transactions")

    # Create a table to display transactions
    tree = ttk.Treeview(transactions_window, columns=("money_source", "amount", "date", "balance_after"), show="headings")
    tree.heading("money_source", text="Money Source")
    tree.heading("amount", text="Amount")
    tree.heading("date", text="Date")
    tree.heading("balance_after", text="Balance After")

    tree.pack(fill="both", expand=True)

    conn = sqlite3.connect('expense_manager.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM money_sources WHERE id=?", (money_source_id,))
    money_source_name = cursor.fetchone()[0]

    cursor.execute("SELECT amount, description, type, money_before, money_after FROM transactions WHERE money_source_id=? ORDER BY id DESC", (money_source_id,))
    transactions = cursor.fetchall()

    for amount, description, type_, money_before, money_after in transactions:
        color = "red" if type_ == "deduct" else "green"
        tree.insert("", "end", values=(money_source_name, f"{amount:.2f}", description, f"{money_after:.2f}"), tags=(color,))

    tree.tag_configure("red", foreground="red")
    tree.tag_configure("green", foreground="green")

    conn.close()


# Retrieve money sources and their balances for displaying
def display_money_sources():
    # Clear the existing money source buttons
    for widget in money_source_frame.winfo_children():
        widget.destroy()

    conn = sqlite3.connect('expense_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, amount FROM money_sources")
    money_sources = cursor.fetchall()
    conn.close()

    for money_source in money_sources:
        money_source_id, name, amount = money_source

        def show_transactions_wrapper(money_source_id):
            return lambda: show_transactions(money_source_id)

        money_source_button = tk.Button(money_source_frame, text=f"{name}: {amount}", command=show_transactions_wrapper(money_source_id))
        money_source_button.pack(fill="x")

    money_source_frame.pack(fill="x")


# Create buttons
add_money_source_button = tk.Button(app, text="Add Money Source", command=add_money_source)
add_transaction_button = tk.Button(app, text="Add Transaction", command=add_transaction)

# Place buttons on the window
add_money_source_button.pack()
add_transaction_button.pack()

# Create a frame to hold money source buttons
money_source_frame = tk.Frame(app)
money_source_frame.pack(fill="x")

display_money_sources()

# Run the main loop
app.mainloop()
