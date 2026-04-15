# 🍽️ Happy Palace — Restaurant POS System

A modern Point of Sale system built for **Happy Palace Restaurant**, written in Python with a dark-themed desktop UI.

---

## Tech Stack

- **Language:** Python 3.x
- **UI:** CustomTkinter (modern dark theme)
- **Database:** SQLite (no server setup needed)

## Features

| Module | Roles |
|---|---|
| 🛒 New Order — table selection, menu grid, cart, discounts | Admin, Cashier, Waiter |
| 🍜 Menu Management — add/edit/delete items & categories | Admin |
| 🪑 Table Management — visual status cards (free/occupied/reserved) | Admin, Cashier |
| 👥 Customer Management — register & search by phone | Admin, Cashier |
| 🏷️ Discount Codes — percentage-based, active/inactive toggle | Admin |
| 📊 Reports — daily sales, net totals, top-selling items | Admin |
| 👤 User Management — create users with role assignment | Admin |

## Roles

- **admin** — full access
- **cashier** — orders, tables, customers
- **waiter** — new orders only

## Getting Started

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Run the app**
```bash
python main.py
```

**3. Default login**
```
Username: admin
Password: admin123
```

> The database (`happy_palace.db`) is created automatically on first run.

## Project Structure

```
happy_palace/
├── main.py          # Entry point
├── database.py      # All DB logic (SQLite)
├── auth.py          # Session state
├── requirements.txt
└── ui/
    ├── login.py
    ├── dashboard.py
    ├── orders.py
    ├── menu_mgmt.py
    ├── tables.py
    ├── customers.py
    ├── discounts.py
    ├── reports.py
    └── users.py
```

## Currency

All prices displayed in **LKR (Sri Lankan Rupee)**.

## Credits

| Name | Field |
|---|---|
| Kulan Silva | Computer Security |
