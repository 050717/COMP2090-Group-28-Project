# Personal Finance Manager

A command-line personal finance management tool built with Python.

## Features

- User registration and login
- Record income and expense transactions
- Set budgets by category
- View monthly reports and budget status

## Project Structure

```
finance/
├── database.py       # Module A – Database setup and connection
├── user.py           # Module A – User management (create, get, delete)
├── transaction.py    # Module A – Transaction CRUD and summary
├── budget.py         # Module B – Budget logic and monthly reports
├── main.py           # Module C – CLI interface and entry point
└── finance.db        # Auto-generated SQLite database
```

## How to Run

```bash
python main.py
```

No external dependencies required — uses Python's built-in `sqlite3` only.

## Team

| Member | Module | Responsibility |
|--------|--------|----------------|
| A | Data Layer | database.py, user.py, transaction.py |
| B | Business Logic | budget.py |
| C | CLI & UX | main.py |
