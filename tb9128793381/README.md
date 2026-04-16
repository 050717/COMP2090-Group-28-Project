Personal Finance Manager



A personal financial management system based on Flask + SQLAlchemy, supporting deposits, withdrawals, transfers, budget management and monthly reports.


Prerequisites

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) 包管理器

Installation and Operation

```bash
# 安装依赖Install dependencies
uv sync

# 迁移旧数据（可选，仅首次运行）Migrate old data (optional, for first run only)
uv run python migrate_data.py

# 启动服务Start the service
uv run python run.py
```

启动后访问 http://localhost:5000 ，默认账号 `root`，密码 `123456`。

Project Structure

```
├── run.py                              #Application Entry
├── migrate_data.py                
├── pyproject.toml                  
├── app/
│   ├── __init__.py                 
│   ├── config.py                   
│   ├── extensions.py              
│   ├── models/                     
│   │   ├── user.py                 
│   │   ├── transaction.py          
│   │   └── budget.py               
│   ├── services/                   
│   │   ├── user_service.py         
│   │   ├── transaction_service.py  
│   │   └── budget_service.py       
│   ├── routes/                    
│   │   ├── auth.py                 
│   │   ├── transaction.py          
│   │   └── budget.py               
│   └── static/                     
│       ├── login.html
│       ├── index.html
│       ├── add-record.html
│       ├── record-list.html
│       ├── change-pwd.html
│       ├── style.css
│       └── app.js
└── raw/                           
```

OOP The use of technology



1. Data Model Layer (Models) - Class Inheritance and Encapsulation
The three model classes User, Transaction, and Budget all inherit from db.Model (the SQLAlchemy declarative base class), embodying inheritance in OOP.
Take User as an example (app/models/user.py):

```python
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, ...}
```

Encapsulation: The password hashing logic is encapsulated in the set_password() and check_password() methods, and external code does not need to know the implementation details of hashing
Inheritance: Inherit from db.Model to obtain ORM query capabilities (such as User.query.filter_by(...))
Class attributes: Declare database fields and constraints using class attributes (db.Column)

API interface

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/register` | 注册 |
| POST | `/api/login` | 登录 |
| POST | `/api/change-password` | 修改密码 |
| GET | `/api/transactions` | 查询交易记录 |
| POST | `/api/transactions` | 新增交易 |
| PUT | `/api/transactions/<id>` | 更新交易 |
| DELETE | `/api/transactions/<id>` | 删除交易 |
| GET | `/api/summary` | 月度汇总 |
| POST | `/api/transfer` | 转账 |
| GET | `/api/budgets` | 查询预算 |
| POST | `/api/budgets` | 设置预算 |
| DELETE | `/api/budgets` | 删除预算 |
| GET | `/api/budget-status` | 预算状态 |
| GET | `/api/monthly-report` | 月度报告 |

Tech stack
Front-end: HTML, CSS, JavaScript
Password Security: werkzeug.security (PBKDF2 哈希)

## Team division of labor
LI Yichen 13786700：Write basic OOP（Encapsulation and inheritance） and extracurricular OOP（Classes and Static）, and configure the Flask environment

SHI Yuanming 13744303 ：Assist in compiling extracurricular OOP and optimize web page functions

YE Zeyang 14146860：Basic web page design and CSS beautification