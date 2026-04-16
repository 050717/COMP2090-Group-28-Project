from datetime import date

from flask import Blueprint, request, jsonify

from app.services.budget_service import BudgetService

budget_bp = Blueprint('budget', __name__)


@budget_bp.route("/api/budgets", methods=["GET"])
def api_get_budgets():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(BudgetService.get_budgets(user_id, month)), 200


@budget_bp.route("/api/budgets", methods=["POST"])
def api_set_budget():
    data = request.json
    try:
        b = BudgetService.set_budget(
            int(data["user_id"]),
            data["category"],
            float(data["amount"]),
            data["month"],
        )
        return jsonify(b), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@budget_bp.route("/api/budgets", methods=["DELETE"])
def api_delete_budget():
    data = request.json
    try:
        ok = BudgetService.delete_budget(
            int(data["user_id"]),
            data["category"],
            data["month"],
        )
        return jsonify({"success": ok}), 200 if ok else 404
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@budget_bp.route("/api/budget-status", methods=["GET"])
def api_budget_status():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(BudgetService.check_status(user_id, month)), 200


@budget_bp.route("/api/monthly-report", methods=["GET"])
def api_monthly_report():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(BudgetService.get_monthly_report(user_id, month)), 200
