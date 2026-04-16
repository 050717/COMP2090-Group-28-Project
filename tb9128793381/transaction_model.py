from datetime import datetime

from app.extensions import db


class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # stored in cents (e.g. $1.23 → 123)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), default="")
    date = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "amount": self.amount / 100,  # convert cents → dollars for frontend
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }
