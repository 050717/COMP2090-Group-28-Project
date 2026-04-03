"""
server.py — Flask REST API bridge
Connects the HTML frontend to the Python backend (database/user/transaction/budget).
Run: python server.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from database import init_db
from user import create_user, get_user_by_username
from transaction import add_transaction, get_transactions, delete_transaction, update_transaction, get_summary
from budget import set_budget, get_budgets, delete_budget, check_budget_status, get_monthly_report
from datetime import date

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ── Init DB on startup ────────────────────────────────────────────────────────
init_db()


# ── Static file serving ───────────────────────────────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(".", "login.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    # Use password as email placeholder (no email field in frontend)
    email = data.get("email") or f"{username}@bank.local"
    try:
        # Store password in a separate simple table
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        # Ensure password column exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        # Check if user already exists
        cursor.execute("SELECT username FROM passwords WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Account already exists"}), 409
        conn.close()

        user = create_user(username, email)

        # Save password
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO passwords (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return jsonify({"id": user["id"], "username": user["username"]}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM passwords WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Account does not exist"}), 404
    if row["password"] != password:
        return jsonify({"error": "Wrong password"}), 401

    user = get_user_by_username(username)
    return jsonify({"id": user["id"], "username": user["username"]}), 200


@app.route("/api/change-password", methods=["POST"])
def api_change_password():
    data = request.json
    username = (data.get("username") or "").strip()
    old_pwd = (data.get("oldPassword") or "").strip()
    new_pwd = (data.get("newPassword") or "").strip()

    if not all([username, old_pwd, new_pwd]):
        return jsonify({"error": "All fields required"}), 400

    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM passwords WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404
    if row["password"] != old_pwd:
        conn.close()
        return jsonify({"error": "Current password is wrong"}), 401

    cursor.execute("UPDATE passwords SET password = ? WHERE username = ?", (new_pwd, username))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200


# ── Transactions ──────────────────────────────────────────────────────────────
@app.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month")  # optional, format YYYY-MM
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    records = get_transactions(user_id, month=month)
    return jsonify(records), 200


@app.route("/api/transactions", methods=["POST"])
def api_add_transaction():
    data = request.json
    try:
        user_id = int(data["user_id"])
        tx_type = data["type"]          # "income" or "expense"
        amount = float(data["amount"])
        category = data.get("category", "General")
        description = data.get("description", "")
        tx_date = data.get("date") or str(date.today())

        t = add_transaction(user_id, tx_type, amount, category, description, tx_date)
        return jsonify(t), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/transactions/<int:txn_id>", methods=["DELETE"])
def api_delete_transaction(txn_id):
    ok = delete_transaction(txn_id)
    if ok:
        return jsonify({"success": True}), 200
    return jsonify({"error": "Not found"}), 404


@app.route("/api/transactions/<int:txn_id>", methods=["PUT"])
def api_update_transaction(txn_id):
    data = request.json
    ok = update_transaction(txn_id, **data)
    return jsonify({"success": ok}), 200 if ok else 404


# ── Summary ───────────────────────────────────────────────────────────────────
@app.route("/api/summary", methods=["GET"])
def api_summary():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    summary = get_summary(user_id, month)
    return jsonify(summary), 200


# ── Transfer (special transaction pair) ──────────────────────────────────────
@app.route("/api/transfer", methods=["POST"])
def api_transfer():
    data = request.json
    try:
        from_user_id = int(data["from_user_id"])
        to_username = data["to_username"].strip()
        amount = float(data["amount"])
        tx_date = data.get("date") or str(date.today())
        description = data.get("description", "")

        # Verify target user exists
        target = get_user_by_username(to_username)
        if not target:
            return jsonify({"error": "Target account not found"}), 404

        from_user = None
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (from_user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            from_user = dict(row)

        if not from_user:
            return jsonify({"error": "Sender not found"}), 404
        if target["id"] == from_user_id:
            return jsonify({"error": "Cannot transfer to yourself"}), 400

        # Check balance
        month = tx_date[:7]
        summary = get_summary(from_user_id, month)
        # Get all-time balance for transfer check
        all_records = get_transactions(from_user_id)
        total_in = sum(float(r["amount"]) for r in all_records if r["type"] == "income")
        total_out = sum(float(r["amount"]) for r in all_records if r["type"] == "expense")
        balance = total_in - total_out
        if amount > balance:
            return jsonify({"error": "Insufficient balance"}), 400

        # Deduct from sender
        add_transaction(from_user_id, "expense", amount, "Transfer",
                        f"To {to_username}{': ' + description if description else ''}", tx_date)
        # Credit to receiver
        add_transaction(target["id"], "income", amount, "Transfer",
                        f"From {from_user['username']}{': ' + description if description else ''}", tx_date)

        return jsonify({"success": True}), 200
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


# ── Budget ────────────────────────────────────────────────────────────────────
@app.route("/api/budgets", methods=["GET"])
def api_get_budgets():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(get_budgets(user_id, month)), 200


@app.route("/api/budgets", methods=["POST"])
def api_set_budget():
    data = request.json
    try:
        b = set_budget(int(data["user_id"]), data["category"], float(data["amount"]), data["month"])
        return jsonify(b), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/budgets", methods=["DELETE"])
def api_delete_budget():
    data = request.json
    ok = delete_budget(int(data["user_id"]), data["category"], data["month"])
    return jsonify({"success": ok}), 200 if ok else 404


@app.route("/api/budget-status", methods=["GET"])
def api_budget_status():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(check_budget_status(user_id, month)), 200


@app.route("/api/monthly-report", methods=["GET"])
def api_monthly_report():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(get_monthly_report(user_id, month)), 200


if __name__ == "__main__":
    print("=" * 50)
    print("  香港大学生银行 — Backend API Server")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
