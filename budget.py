from database import get_connection
from transaction import get_summary


def set_budget(user_id: int, category: str, amount: float, month: str) -> dict:
    """
    Set or update a budget for a category in a given month.
    month format: 'YYYY-MM'
    """
    if amount <= 0:
        raise ValueError("Budget amount must be positive")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO budgets (user_id, category, amount, month)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, category, month)
           DO UPDATE SET amount = excluded.amount""",
        (user_id, category, amount, month)
    )
    conn.commit()
    conn.close()
    return {"user_id": user_id, "category": category, "amount": amount, "month": month}


def get_budgets(user_id: int, month: str) -> list:
    """Return all budgets for a user in a given month."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM budgets WHERE user_id = ? AND month = ?",
        (user_id, month)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_budget(user_id: int, category: str, month: str) -> bool:
    """Delete a specific budget entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
        (user_id, category, month)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def check_budget_status(user_id: int, month: str) -> list:
    """
    Compare actual spending vs budget for each category.
    Returns a list of status dicts per category.
    """
    budgets = get_budgets(user_id, month)
    summary = get_summary(user_id, month)
    actual_by_category = summary.get("by_category", {})

    results = []
    for b in budgets:
        category = b["category"]
        budget_amount = b["amount"]
        spent = actual_by_category.get(category, 0.0)
        remaining = round(budget_amount - spent, 2)
        percent_used = round((spent / budget_amount) * 100, 1) if budget_amount > 0 else 0

        results.append({
            "category": category,
            "budget": budget_amount,
            "spent": spent,
            "remaining": remaining,
            "percent_used": percent_used,
            "over_budget": spent > budget_amount
        })

    return results


def get_monthly_report(user_id: int, month: str) -> dict:
    """
    Generate a full monthly financial report including:
    - income / expense / balance
    - budget status per category
    - overall budget health
    """
    summary = get_summary(user_id, month)
    budget_status = check_budget_status(user_id, month)

    over_budget_categories = [b["category"] for b in budget_status if b["over_budget"]]

    return {
        "month": month,
        "income": summary["income"],
        "expense": summary["expense"],
        "balance": summary["balance"],
        "budget_status": budget_status,
        "over_budget_categories": over_budget_categories,
        "is_healthy": len(over_budget_categories) == 0
    }
