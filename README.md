OTHER OOP and extra use


#业务逻辑层 (Services) - Classes and static methods
```python
class UserService:
    @staticmethod
    def create_user(username, email, password):
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
Separation of Duties: UserService handles user logic, TransactionService handles transaction logic, and BudgetService handles budget logic
Classes as Namespaces: Use classes to organize related methods and avoid scattered global functions

Configuration Class
```python
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///finance.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev-secret-key"
```
Manage configuration items using class attributes and load them 'via app.config.from_object(Config)'.

Tech stack
-Backend: Flask, Flask-SQLAlchemy, Flask-CORS
-Database: SQLite