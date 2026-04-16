import datetime

from app.extensions import db
from app.models import Transaction, User


class TransactionService:

    @staticmethod
    def add(user_id, type, amount, category, description='', date=None):
        if type not in ('income', 'expense'):
            raise ValueError("type must be 'income' or 'expense'.")
        if amount <= 0:
            raise ValueError("amount must be greater than 0.")

        # Convert to cents (integer) to avoid float precision issues
        amount_cents = round(amount * 100)

        # Balance check for withdrawals
        if type == 'expense':
            all_txns = Transaction.query.filter_by(user_id=user_id).all()
            total_income = sum(t.amount for t in all_txns if t.type == 'income')
            total_expense = sum(t.amount for t in all_txns if t.type == 'expense')
            balance = total_income - total_expense  # all integers, no float error
            if amount_cents > balance:
                raise ValueError("Insufficient balance.")

        if date is None:
            date = str(datetime.date.today())

        txn = Transaction(
            user_id=user_id,
            type=type,
            amount=amount_cents,
            category=category,
            description=description,
            date=date,
        )
        db.session.add(txn)
        db.session.commit()
        return txn.to_dict()

    @staticmethod
    def get_list(user_id, month=None, type=None):
        query = Transaction.query.filter_by(user_id=user_id)
        if month is not None:
            query = query.filter(Transaction.date.like(month + '%'))
        if type is not None:
            query = query.filter_by(type=type)
        return [t.to_dict() for t in query.order_by(Transaction.date.desc()).all()]

    @staticmethod
    def update(txn_id, **kwargs):
        txn = Transaction.query.get(txn_id)
        if not txn:
            return False
        allowed = {'amount', 'category', 'description', 'date'}
        for key, value in kwargs.items():
            if key in allowed:
                if key == 'amount':
                    setattr(txn, key, round(float(value) * 100))
                else:
                    setattr(txn, key, value)
        db.session.commit()
        return True

    @staticmethod
    def delete(txn_id):
        txn = Transaction.query.get(txn_id)
        if not txn:
            return False
        db.session.delete(txn)
        db.session.commit()
        return True

    @staticmethod
    def get_summary(user_id, month):
        txns = Transaction.query.filter_by(user_id=user_id).filter(
            Transaction.date.like(month + '%')
        ).all()
        # All integer arithmetic — no float error
        total_income_cents = sum(t.amount for t in txns if t.type == 'income')
        total_expense_cents = sum(t.amount for t in txns if t.type == 'expense')
        by_category = {}
        for t in txns:
            if t.type == 'expense':
                by_category[t.category] = by_category.get(t.category, 0) + t.amount
        return {
            'income': total_income_cents / 100,
            'expense': total_expense_cents / 100,
            'balance': (total_income_cents - total_expense_cents) / 100,
            'by_category': {k: v / 100 for k, v in by_category.items()},
        }

    @staticmethod
    def transfer(from_user_id, to_username, amount, date=None, description=''):
        target = User.query.filter_by(username=to_username).first()
        if not target:
            raise ValueError(f"User '{to_username}' not found.")
        if target.id == from_user_id:
            raise ValueError("Cannot transfer to yourself.")

        amount_cents = round(amount * 100)

        all_txns = Transaction.query.filter_by(user_id=from_user_id).all()
        total_income = sum(t.amount for t in all_txns if t.type == 'income')
        total_expense = sum(t.amount for t in all_txns if t.type == 'expense')
        balance = total_income - total_expense  # integer arithmetic
        if amount_cents > balance:
            raise ValueError("Insufficient balance.")

        if date is None:
            date = str(datetime.date.today())

        sender = User.query.get(from_user_id)
        sender_username = sender.username if sender else str(from_user_id)

        expense_txn = Transaction(
            user_id=from_user_id,
            type='expense',
            amount=amount_cents,
            category='Transfer',
            description=f"To {to_username}: {description}",
            date=date,
        )
        income_txn = Transaction(
            user_id=target.id,
            type='income',
            amount=amount_cents,
            category='Transfer',
            description=f"From {sender_username}: {description}",
            date=date,
        )
        db.session.add(expense_txn)
        db.session.add(income_txn)
        db.session.commit()
        return True
