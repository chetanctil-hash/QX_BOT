import sqlite3
import ast
import os
from datetime import datetime

def migrate():
    """
    Migrates the static PF_BASE list from index.py to the portfolio database table.
    """
    index_file_path = "index.py"
    db_path = "qx_terminal.db"

    if not os.path.exists(index_file_path):
        print(f"Error: {index_file_path} not found.")
        return

    print(f"Reading static portfolio from {index_file_path}...")

    # Extract PF_BASE using simple string parsing to avoid executing the whole file
    with open(index_file_path, "r") as f:
        content = f.read()

    try:
        # Find the start and end of the PF_BASE list
        start_idx = content.find("PF_BASE = [") + len("PF_BASE = [")
        end_idx = content.find("]", start_idx) + 1
        list_str = "[" + content[start_idx:end_idx]

        # Safely evaluate the string as a Python list
        pf_base = ast.literal_eval(list_str)
        print(f"Found {len(pf_base)} positions in PF_BASE.")
    except Exception as e:
        print(f"Error parsing PF_BASE: {e}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Ensure instruments table has these symbols
        for item in pf_base:
            sym = item['sym']
            cursor.execute(
                "INSERT OR IGNORE INTO instruments (symbol, last_updated) VALUES (?, ?)",
                (sym, datetime.now().isoformat())
            )

        # 2. Insert into portfolio table
        for item in pf_base:
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio (symbol, quantity, avg_cost, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (
                item['sym'],
                item['qty'],
                item['avg'],
                datetime.now().isoformat()
            ))

        conn.commit()
        print("Migration successful: PF_BASE moved to qx_terminal.db")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
