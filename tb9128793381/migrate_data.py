"""
migrate_cents.py
Run once to convert existing float amounts → integer cents in the database.
Usage: python migrate_cents.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "finance.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id, amount FROM \"transaction\"")
rows = cur.fetchall()

print(f"Migrating {len(rows)} records...")
for row_id, amount in rows:
    cents = round(float(amount) * 100)
    cur.execute("UPDATE \"transaction\" SET amount = ? WHERE id = ?", (cents, row_id))
    print(f"  id={row_id}: {amount} → {cents} cents")

conn.commit()
conn.close()
print("Migration complete.")
