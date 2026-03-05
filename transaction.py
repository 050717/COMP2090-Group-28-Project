from database import get_connection
from datetime import date as today


def add_transaction(user_id: int, type: str, amount: float,
                    category: str, description: str = "", date: str = None) -> dict:
    """Add an income or expense transaction."""
    if type not in ("income", "expense"):
        raise ValueError("type must be 'income' or 'expense'")
    if amount <= 0:
        raise ValueError("amount must be a positive number")
    if date is None:
        date = str(today.today())

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
    return {
        "id": txn_id, "user_id": user_id, "type": type,
        "amount": amount, "category": category,
        "description": description, "date": date
    }


def get_transactions(user_id: int, month: str = None, type: str = None) -> list:
    """
    Return transactions for a user.
    month format: 'YYYY-MM'  e.g. '2025-03'
    type: 'income' or 'expense' (optional filter)
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]

    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)
    if type:
        query += " AND type = ?"
        params.append(type)

    query += " ORDER BY date DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_transaction(txn_id: int, **kwargs) -> bool:
    """Update fields of a transaction. Supports: amount, category, description, date."""
    allowed = {"amount", "category", "description", "date"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return False

    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    cursor.execute(
        f"UPDATE transactions SET {set_clause} WHERE id = ?",
        list(updates.values()) + [txn_id]
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_transaction(txn_id: int) -> bool:
    """Delete a transaction by ID. Returns True if deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_summary(user_id: int, month: str) -> dict:
    """
    Return income/expense/balance summary for a given month.
    Also returns breakdown by category.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Total income and expense
    cursor.execute(
        """SELECT type, SUM(amount) as total FROM transactions
           WHERE user_id = ? AND strftime('%Y-%m', date) = ?
           GROUP BY type""",
        (user_id, month)
    )
    rows = cursor.fetchall()
    summary = {"income": 0.0, "expense": 0.0}
    for row in rows:
        summary[row["type"]] = round(row["total"], 2)
    summary["balance"] = round(summary["income"] - summary["expense"], 2)

    # Breakdown by category (expense only)
    cursor.execute(
        """SELECT category, SUM(amount) as total FROM transactions
           WHERE user_id = ? AND type = 'expense'
           AND strftime('%Y-%m', date) = ?
           GROUP BY category ORDER BY total DESC""",
        (user_id, month)
    )
    category_rows = cursor.fetchall()
    summary["by_category"] = {row["category"]: round(row["total"], 2) for row in category_rows}

    conn.close()
    return summary
