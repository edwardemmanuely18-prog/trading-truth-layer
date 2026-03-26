import sqlite3
from app.core.security import hash_password

conn = sqlite3.connect("trading_truth_layer.db")
cur = conn.cursor()

# operator password
cur.execute(
    "UPDATE users SET password_hash=? WHERE email=?",
    (hash_password("OperatorPass123!"), "operator@tradingtruthlayer.com"),
)

# member password
cur.execute(
    "UPDATE users SET password_hash=? WHERE email=?",
    (hash_password("MemberPass123!"), "member1@example.com"),
)

conn.commit()
conn.close()

print("Passwords updated successfully.")