from flask import Blueprint, request, jsonify

from app.services.user_service import UserService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    email = data.get("email") or f"{username}@bank.local"
    try:
        user = UserService.create_user(username, email, password)
        return jsonify({"id": user["id"], "username": user["username"]}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Check if user exists first
    user_record = UserService.get_by_username(username)
    if not user_record:
        return jsonify({"error": "Account does not exist"}), 404

    result = UserService.authenticate(username, password)
    if result is None:
        return jsonify({"error": "Wrong password"}), 401

    return jsonify({"id": result["id"], "username": result["username"]}), 200


@auth_bp.route("/api/change-password", methods=["POST"])
def api_change_password():
    data = request.json
    username = (data.get("username") or "").strip()
    old_pwd = (data.get("oldPassword") or "").strip()
    new_pwd = (data.get("newPassword") or "").strip()

    if not all([username, old_pwd, new_pwd]):
        return jsonify({"error": "All fields required"}), 400

    try:
        UserService.change_password(username, old_pwd, new_pwd)
        return jsonify({"success": True}), 200
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 401
