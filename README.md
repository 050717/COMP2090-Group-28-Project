# 香港大学生银行 — Personal Finance Manager

A full-stack personal finance web application built with Python (Flask) and vanilla HTML/CSS/JS, backed by SQLite.

## Features

- User registration and login with session management
- Deposit, withdraw, and transfer between accounts
- Real-time account balance calculation
- Transaction history with delete support
- Set budgets by category
- Monthly financial reports and budget status
- Background images for dashboard and transaction pages

## Project Structure

```
pjct/
├── server.py         # Flask REST API server + static file serving
├── database.py       # Database setup and SQLite connection
├── user.py           # User management (create, get, delete)
├── transaction.py    # Transaction CRUD and monthly summary
├── budget.py         # Budget logic and monthly reports
├── main.py           # (Legacy) CLI interface
├── index.html        # Dashboard
├── login.html        # Login / Register
├── add-record.html   # New transaction form
├── record-list.html  # Transaction history
├── change-pwd.html   # Change password
├── app.js            # Frontend logic (API calls, session management)
├── style.css         # Stylesheet
├── hongkong.jpg      # Dashboard background
├── atm.jpg           # Transaction page background
└── finance.db        # Auto-generated SQLite database
```

## How to Run

**Requirements:** Python 3.8+

Install dependencies:
```bash
pip3 install flask flask-cors
```

Start the server:
```bash
python3 server.py
```

Then open your browser and go to: **http://localhost:5000**

`finance.db` is created automatically on first launch — no setup required.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register a new account |
| POST | `/api/login` | Login |
| POST | `/api/change-password` | Change password |
| GET | `/api/transactions` | Get all transactions |
| POST | `/api/transactions` | Add a transaction |
| DELETE | `/api/transactions/<id>` | Delete a transaction |
| POST | `/api/transfer` | Transfer between accounts |
| GET | `/api/summary` | Income/expense summary |
| GET/POST | `/api/budgets` | Get or set budgets |
| GET | `/api/budget-status` | Budget vs actual spending |
| GET | `/api/monthly-report` | Full monthly report |

## Team

| Member | Module | Responsibility |
|--------|--------|----------------|
| A | Data Layer | database.py, user.py, transaction.py |
| B | Business Logic | budget.py |
| C | CLI & UX | main.py, server.py, frontend |
