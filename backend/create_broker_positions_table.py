# backend/create_broker_positions_table.py

import sqlite3

conn = sqlite3.connect(
    "backend/trading_truth_layer.db"
)

conn.execute("""
CREATE TABLE IF NOT EXISTS broker_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    broker TEXT NOT NULL,
    account_id TEXT NOT NULL,

    symbol TEXT NOT NULL,

    quantity REAL NOT NULL,

    avg_cost REAL,
    mark_price REAL,

    position_value REAL,

    unrealized_pnl REAL,

    last_synced_at TEXT
)
""")

conn.commit()

print("broker_positions created")