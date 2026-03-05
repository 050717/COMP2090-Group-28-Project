from database import get_connection
from datetime import date as date_type


def add_transaction(user_id: int, type: str, amount: float,
                    category: str, description: str = "", date: str = None) -> dict:
    if type not in ("income", "expense"):
        raise ValueError("type must be 'income' or 'expense'")
    if amount <= 0:
        raise ValueError("amount must be positive")
    if date is None:
        date = str(date_type.today())

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO transactions (user_id, type, amount, category, description, date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, type, amount, category, description, date)
    )
    conn.commit()
    txn_id = cursor.lastrowid
    conn.close()
    return {"id": txn_id, "user_id": user_id, "type": type,
            "amount": amount, "category": category, "date": date}


def get_transactions(user_id: int, month: str = None) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    if month:
        cursor.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND strftime('%Y-%m', date) = ? ORDER BY date DESC",
            (user_id, month)
        )
    else:
        cursor.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_transaction(txn_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_summary(user_id: int, month: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT type, SUM(amount) as total FROM transactions
           WHERE user_id = ? AND strftime('%Y-%m', date) = ?
           GROUP BY type""",
        (user_id, month)
    )
    rows = cursor.fetchall()
    conn.close()

    summary = {"income": 0.0, "expense": 0.0}
    for row in rows:
        summary[row["type"]] = row["total"]
    summary["balance"] = summary["income"] - summary["expense"]
    return summary
