import sqlite3

DB_PATH = "trading_truth_layer.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

columns = [
    "description TEXT",
    "billing_email TEXT",
    "plan_code TEXT DEFAULT 'starter'",
    "billing_status TEXT DEFAULT 'inactive'",
    "stripe_customer_id TEXT",
    "stripe_subscription_id TEXT",
    "subscription_current_period_end DATETIME",
    "claim_limit INTEGER DEFAULT 5",
    "trade_limit INTEGER DEFAULT 1000",
    "member_limit INTEGER DEFAULT 3",
    "storage_limit_mb INTEGER DEFAULT 500",
    "created_at DATETIME",
    "updated_at DATETIME",
]

for col in columns:
    name = col.split()[0]

    try:
        cursor.execute(f"ALTER TABLE workspaces ADD COLUMN {col}")
        print(f"Added column: {name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column already exists: {name}")
        else:
            raise

cursor.execute(
    """
    UPDATE workspaces
    SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
        updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
    """
)

conn.commit()
conn.close()

print("\nWorkspace table migration complete.")