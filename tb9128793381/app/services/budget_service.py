import datetime

from app.extensions import db
from app.models import Budget, Transaction


class BudgetService:

    @staticmethod
    def set_budget(user_id, category, amount, month):
        existing = Budget.query.filter_by(
            user_id=user_id, category=category, month=month
        ).first()
        if existing:
            existing.amount = amount
            db.session.commit()
            return existing.to_dict()
        budget = Budget(user_id=user_id, category=category, amount=amount, month=month)
        db.session.add(budget)
        db.session.commit()
        return budget.to_dict()

    @staticmethod
    def get_budgets(user_id, month=None):
        if month is None:
            month = str(datetime.date.today())[:7]
        return [b.to_dict() for b in Budget.query.filter_by(user_id=user_id, month=month).all()]

    @staticmethod
    def delete_budget(user_id, category, month):
        budget = Budget.query.filter_by(
            user_id=user_id, category=category, month=month
        ).first()
        if not budget:
            return False
        db.session.delete(budget)
        db.session.commit()
        return True

    @staticmethod
    def check_status(user_id, month):
        budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
        txns = Transaction.query.filter_by(user_id=user_id).filter(
            Transaction.date.like(month + '%')
        ).all()
        spent_by_category = {}
        for t in txns:
            if t.type == 'expense':
                spent_by_category[t.category] = spent_by_category.get(t.category, 0) + t.amount
        result = []
        for b in budgets:
            spent = spent_by_category.get(b.category, 0)
            result.append({
                'category': b.category,
                'budget': b.amount,
                'spent': spent,
                'remaining': b.amount - spent,
                'over_budget': spent > b.amount,
            })
        return result

    @staticmethod
    def get_monthly_report(user_id, month):
        budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
        txns = Transaction.query.filter_by(user_id=user_id).filter(
            Transaction.date.like(month + '%')
        ).all()
        total_income = sum(t.amount for t in txns if t.type == 'income')
        total_expense = sum(t.amount for t in txns if t.type == 'expense')
        spent_by_category = {}
        for t in txns:
            if t.type == 'expense':
                spent_by_category[t.category] = spent_by_category.get(t.category, 0) + t.amount
        budget_status = []
        for b in budgets:
            spent = spent_by_category.get(b.category, 0)
            budget_status.append({
                'category': b.category,
                'budget': b.amount,
                'spent': spent,
                'remaining': b.amount - spent,
                'over_budget': spent > b.amount,
            })
        return {
            'month': month,
            'income': total_income,
            'expense': total_expense,
            'balance': total_income - total_expense,
            'budget_status': budget_status,
        }
