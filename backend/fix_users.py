import sqlite3

conn = sqlite3.connect("trading_truth_layer.db")
cur = conn.cursor()

cur.execute("UPDATE users SET email=? WHERE id=1", ("owner@tradingtruthlayer.com",))
cur.execute("UPDATE users SET email=? WHERE id=2", ("operator@tradingtruthlayer.com",))

conn.commit()

rows = cur.execute("SELECT id, email FROM users WHERE id IN (1,2)").fetchall()
print("Updated users:", rows)

conn.close()