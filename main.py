import sys
from database import init_db
from user import create_user, get_user_by_username
from transaction import add_transaction, get_transactions, delete_transaction, get_summary
from budget import set_budget, check_budget_status, get_monthly_report
from datetime import date


# ── Helpers ──────────────────────────────────────────────────────────────────

def print_line():
    print("-" * 50)

def current_month():
    return date.today().strftime("%Y-%m")

def require_login() -> dict:
    username = input("Enter your username: ").strip()
    user = get_user_by_username(username)
    if not user:
        print(f"User '{username}' not found.")
        sys.exit(1)
    print(f"Welcome back, {user['username']}!")
    return user


# ── Menus ─────────────────────────────────────────────────────────────────────

def menu_transactions(user):
    while True:
        print_line()
        print("TRANSACTIONS")
        print("1. Add income")
        print("2. Add expense")
        print("3. View this month's transactions")
        print("4. View all transactions")
        print("5. Delete a transaction")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            amount = float(input("Amount: "))
            category = input("Category (e.g. Salary, Freelance): ").strip()
            desc = input("Description (optional): ").strip()
            t = add_transaction(user["id"], "income", amount, category, desc)
            print(f"Added income: ${t['amount']} [{t['category']}]")

        elif choice == "2":
            amount = float(input("Amount: "))
            category = input("Category (e.g. Food, Rent, Transport): ").strip()
            desc = input("Description (optional): ").strip()
            t = add_transaction(user["id"], "expense", amount, category, desc)
            print(f"Added expense: ${t['amount']} [{t['category']}]")

        elif choice == "3":
            month = current_month()
            records = get_transactions(user["id"], month=month)
            print(f"\n--- {month} Transactions ({len(records)} records) ---")
            for r in records:
                sign = "+" if r["type"] == "income" else "-"
                print(f"  [{r['id']}] {r['date']}  {sign}${r['amount']:<10} {r['category']:<15} {r['description']}")

        elif choice == "4":
            records = get_transactions(user["id"])
            print(f"\n--- All Transactions ({len(records)} records) ---")
            for r in records:
                sign = "+" if r["type"] == "income" else "-"
                print(f"  [{r['id']}] {r['date']}  {sign}${r['amount']:<10} {r['category']:<15} {r['description']}")

        elif choice == "5":
            txn_id = int(input("Transaction ID to delete: "))
            if delete_transaction(txn_id):
                print("Transaction deleted.")
            else:
                print("Transaction not found.")

        elif choice == "0":
            break


def menu_budget(user):
    while True:
        print_line()
        print("BUDGET")
        print("1. Set budget for a category")
        print("2. Check budget status (this month)")
        print("3. Full monthly report")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            category = input("Category: ").strip()
            amount = float(input("Budget amount: "))
            month = input(f"Month (YYYY-MM) [default: {current_month()}]: ").strip() or current_month()
            b = set_budget(user["id"], category, amount, month)
            print(f"Budget set: {b['category']} = ${b['amount']} for {b['month']}")

        elif choice == "2":
            month = current_month()
            statuses = check_budget_status(user["id"], month)
            if not statuses:
                print("No budgets set for this month.")
            else:
                print(f"\n--- Budget Status for {month} ---")
                for s in statuses:
                    flag = "⚠ OVER" if s["over_budget"] else "✓ OK"
                    print(f"  {flag}  {s['category']:<15} Budget: ${s['budget']:<8} Spent: ${s['spent']:<8} Remaining: ${s['remaining']}")

        elif choice == "3":
            month = input(f"Month (YYYY-MM) [default: {current_month()}]: ").strip() or current_month()
            report = get_monthly_report(user["id"], month)
            print(f"\n===== Monthly Report: {report['month']} =====")
            print(f"  Income:   ${report['income']}")
            print(f"  Expense:  ${report['expense']}")
            print(f"  Balance:  ${report['balance']}")
            print(f"  Health:   {'Healthy ✓' if report['is_healthy'] else 'Over budget in: ' + ', '.join(report['over_budget_categories'])}")
            print(f"\n  Budget breakdown:")
            for s in report["budget_status"]:
                flag = "⚠" if s["over_budget"] else "✓"
                print(f"    {flag} {s['category']:<15} {s['percent_used']}% used  (${s['spent']} / ${s['budget']})")

        elif choice == "0":
            break


def main_menu(user):
    while True:
        print_line()
        print(f"PERSONAL FINANCE MANAGER  |  User: {user['username']}")
        print("1. Transactions")
        print("2. Budget & Reports")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            menu_transactions(user)
        elif choice == "2":
            menu_budget(user)
        elif choice == "0":
            print("Goodbye!")
            break


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    print_line()
    print("PERSONAL FINANCE MANAGER")
    print("1. Login")
    print("2. Register")
    choice = input("Choose: ").strip()

    if choice == "2":
        username = input("New username: ").strip()
        email = input("Email: ").strip()
        try:
            user = create_user(username, email)
            print(f"Account created! Welcome, {user['username']}.")
        except ValueError as e:
            print(str(e))
            sys.exit(1)
    else:
        user = require_login()

    main_menu(user)
