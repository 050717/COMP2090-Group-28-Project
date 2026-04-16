from datetime import date

from flask import Blueprint, request, jsonify

from app.services.transaction_service import TransactionService

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    records = TransactionService.get_list(user_id, month=month)
    return jsonify(records), 200


@transaction_bp.route("/api/transactions", methods=["POST"])
def api_add_transaction():
    data = request.json
    try:
        user_id = int(data["user_id"])
        tx_type = data["type"]
        amount = float(data["amount"])
        category = data.get("category", "General")
        description = data.get("description", "")
        tx_date = data.get("date") or str(date.today())
        t = TransactionService.add(user_id, tx_type, amount, category, description, tx_date)
        return jsonify(t), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@transaction_bp.route("/api/transactions/<int:txn_id>", methods=["PUT"])
def api_update_transaction(txn_id):
    data = request.json
    ok = TransactionService.update(txn_id, **data)
    return jsonify({"success": ok}), 200 if ok else 404


@transaction_bp.route("/api/transactions/<int:txn_id>", methods=["DELETE"])
def api_delete_transaction(txn_id):
    ok = TransactionService.delete(txn_id)
    if ok:
        return jsonify({"success": True}), 200
    return jsonify({"error": "Not found"}), 404


@transaction_bp.route("/api/summary", methods=["GET"])
def api_summary():
    user_id = request.args.get("user_id", type=int)
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    summary = TransactionService.get_summary(user_id, month)
    return jsonify(summary), 200


@transaction_bp.route("/api/transfer", methods=["POST"])
def api_transfer():
    data = request.json
    try:
        from_user_id = int(data["from_user_id"])
        to_username = data["to_username"].strip()
        amount = float(data["amount"])
        tx_date = data.get("date") or str(date.today())
        description = data.get("description", "")
        TransactionService.transfer(from_user_id, to_username, amount, tx_date, description)
        return jsonify({"success": True}), 200
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return jsonify({"error": msg}), 404
        if "yourself" in msg.lower() or "insufficient" in msg.lower():
            return jsonify({"error": msg}), 400
        return jsonify({"error": msg}), 400
    except (KeyError,) as e:
        return jsonify({"error": str(e)}), 400
