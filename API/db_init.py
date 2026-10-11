import os
import sqlite3
from datetime import datetime

def init_db():
    """Initialize the QX Terminal database schema."""
    db_path = "qx_terminal.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Instrument Master: Core stock definitions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            cluster TEXT,
            market_cap_cr REAL,
            is_eligible BOOLEAN DEFAULT 1,
            last_updated DATETIME
        )
    ''')

    # 2. Daily Bars: Point-in-time price data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_bars (
            symbol TEXT,
            date DATE,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date),
            FOREIGN KEY (symbol) REFERENCES instruments (symbol)
        )
    ''')

    # 3. Signal Snapshots: Immutable record of scores (The Learning Ledger)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signal_snapshots (
            signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            timestamp DATETIME,
            regime TEXT,
            mom_score REAL,
            earnings_score REAL,
            entry_score REAL,
            composite_score REAL,
            action TEXT,
            signal_price REAL,
            data_coverage REAL,
            data_confidence TEXT,
            outcome_return_1m REAL,
            outcome_status TEXT,
            FOREIGN KEY (symbol) REFERENCES instruments (symbol)
        )
    ''')

    # 4. Portfolio: User holdings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            symbol TEXT PRIMARY KEY,
            quantity REAL,
            avg_cost REAL,
            last_updated DATETIME,
            FOREIGN KEY (symbol) REFERENCES instruments (symbol)
        )
    ''')

    # 5. Configuration: Versioned strategy weights
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategy_config (
            version TEXT PRIMARY KEY,
            mom_weight REAL,
            earnings_weight REAL,
            val_weight REAL,
            risk_weight REAL,
            created_at DATETIME
        )
    ''')

    # 6. Rejected Candidates: Audit trail for false negatives
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rejected_candidates (
            rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            timestamp DATETIME,
            filter_failed TEXT,
            reason TEXT,
            price_at_rejection REAL,
            FOREIGN KEY (symbol) REFERENCES instruments (symbol)
        )
    ''')


if __name__ == "__main__":
    init_db()
