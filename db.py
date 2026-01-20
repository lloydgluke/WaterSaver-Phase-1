import sqlite3

DB_NAME = "watersaver.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # --- Users table: now includes BOTH daily + monthly budget
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            town TEXT,
            restriction_level TEXT,
            daily_budget_litres REAL,
            monthly_budget_litres REAL
        )
    """)

    # --- Zones table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            name TEXT,
            area REAL,
            sprinklers INTEGER,
            flow_rate REAL,
            source TEXT,
            custom_pressure REAL
        )
    """)

    # --- Usage table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            date TEXT,
            zone_name TEXT,
            duration REAL,
            water_used REAL
        )
    """)

    conn.commit()
    conn.close()
