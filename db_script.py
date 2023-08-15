import sqlite3

# Connect to the database (creates if doesn't exist)
conn = sqlite3.connect('expense_manager.db')
cursor = conn.cursor()

# Create the money_sources table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS money_sources (
        id INTEGER PRIMARY KEY,
        name TEXT,
        amount REAL,
        description TEXT
    )
''')

# Create the transactions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        amount REAL,
        money_source_id INTEGER,
        description TEXT,
        type TEXT,
        money_before REAL,
        money_after REAL,
        FOREIGN KEY (money_source_id) REFERENCES money_sources (id)
    )
''')

conn.commit()
conn.close()
