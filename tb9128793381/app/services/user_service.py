from app.extensions import db
from app.models import User


class UserService:

    @staticmethod
    def create_user(username, email, password):
        if User.query.filter_by(username=username).first():
            raise ValueError(f"Username '{username}' already exists.")
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user.to_dict()
        return None

    @staticmethod
    def change_password(username, old_password, new_password):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError(f"User '{username}' not found.")
        if not user.check_password(old_password):
            raise ValueError("Old password is incorrect.")
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def get_by_username(username):
        user = User.query.filter_by(username=username).first()
        return user.to_dict() if user else None

    @staticmethod
    def get_by_id(user_id):
        user = User.query.get(user_id)
        return user.to_dict() if user else None
