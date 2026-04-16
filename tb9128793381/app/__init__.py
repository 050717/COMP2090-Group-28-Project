from flask import Flask, send_from_directory
from flask_cors import CORS
from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.transaction import transaction_bp
    from app.routes.budget import budget_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(budget_bp)

    # Static file serving for frontend
    @app.route("/")
    def serve_index():
        return send_from_directory(app.static_folder, "login.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    with app.app_context():
        from app.models import User, Transaction, Budget  # ensure models registered
        db.create_all()

    return app
