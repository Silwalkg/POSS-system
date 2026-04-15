import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "happy_palace.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','cashier','waiter')),
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                price REAL NOT NULL,
                available INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER UNIQUE NOT NULL,
                status TEXT DEFAULT 'free' CHECK(status IN ('free','occupied','reserved'))
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                email TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS discounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                percentage REAL NOT NULL CHECK(percentage > 0 AND percentage <= 100),
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER REFERENCES tables(id),
                customer_id INTEGER REFERENCES customers(id),
                cashier TEXT NOT NULL,
                discount_id INTEGER REFERENCES discounts(id),
                subtotal REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                total REAL NOT NULL,
                status TEXT DEFAULT 'paid' CHECK(status IN ('open','paid','cancelled')),
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER REFERENCES orders(id),
                menu_item_id INTEGER REFERENCES menu_items(id),
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            );
        """)

        # seed default admin
        cur = conn.execute("SELECT id FROM users WHERE username='admin'")
        if not cur.fetchone():
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", hash_password("admin123"), "admin")
            )

        # seed sample categories
        for cat in ["Rice & Curry", "Short Eats", "Beverages", "Desserts"]:
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

        # seed sample tables
        for n in range(1, 11):
            conn.execute("INSERT OR IGNORE INTO tables (number) VALUES (?)", (n,))

        # seed sample menu items
        sample_items = [
            ("Rice & Curry",  [("Rice & Curry Plate", 350), ("Chicken Curry Rice", 450), ("Fish Curry Rice", 420)]),
            ("Short Eats",    [("Vegetable Roti", 80), ("Egg Roti", 100), ("Chicken Patty", 120), ("Fish Bun", 90)]),
            ("Beverages",     [("Plain Tea", 60), ("Milk Tea", 80), ("Mango Juice", 150), ("Soft Drink", 120)]),
            ("Desserts",      [("Watalappan", 180), ("Ice Cream", 200), ("Fruit Salad", 160)]),
        ]
        for cat_name, items in sample_items:
            cat = conn.execute("SELECT id FROM categories WHERE name=?", (cat_name,)).fetchone()
            if cat:
                for item_name, price in items:
                    conn.execute(
                        "INSERT OR IGNORE INTO menu_items (name, category_id, price) VALUES (?,?,?)",
                        (item_name, cat["id"], price)
                    )

        conn.commit()


# ── Auth ──────────────────────────────────────────────────────────────────────

def login_user(username: str, password: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        ).fetchone()
    return dict(row) if row else None


# ── Users ─────────────────────────────────────────────────────────────────────

def get_all_users():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT id,username,role,created_at FROM users").fetchall()]

def create_user(username, password, role):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username,password,role) VALUES (?,?,?)",
            (username, hash_password(password), role)
        )
        conn.commit()

def delete_user(user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()


# ── Categories ────────────────────────────────────────────────────────────────

def get_categories():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM categories").fetchall()]

def add_category(name):
    with get_conn() as conn:
        conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()

def delete_category(cat_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit()


# ── Menu Items ────────────────────────────────────────────────────────────────

def get_menu_items(category_id=None, available_only=True):
    with get_conn() as conn:
        query = """
            SELECT m.*, c.name as category_name
            FROM menu_items m
            LEFT JOIN categories c ON m.category_id = c.id
            WHERE 1=1
        """
        params = []
        if available_only:
            query += " AND m.available=1"
        if category_id:
            query += " AND m.category_id=?"
            params.append(category_id)
        query += " ORDER BY c.name, m.name"
        return [dict(r) for r in conn.execute(query, params).fetchall()]

def add_menu_item(name, category_id, price):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO menu_items (name,category_id,price) VALUES (?,?,?)",
            (name, category_id, price)
        )
        conn.commit()

def update_menu_item(item_id, name, category_id, price, available):
    with get_conn() as conn:
        conn.execute(
            "UPDATE menu_items SET name=?,category_id=?,price=?,available=? WHERE id=?",
            (name, category_id, price, available, item_id)
        )
        conn.commit()

def delete_menu_item(item_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
        conn.commit()


# ── Tables ────────────────────────────────────────────────────────────────────

def get_tables():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM tables ORDER BY number").fetchall()]

def set_table_status(table_id, status):
    with get_conn() as conn:
        conn.execute("UPDATE tables SET status=? WHERE id=?", (status, table_id))
        conn.commit()

def add_table(number):
    with get_conn() as conn:
        conn.execute("INSERT INTO tables (number) VALUES (?)", (number,))
        conn.commit()

def delete_table(table_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM tables WHERE id=?", (table_id,))
        conn.commit()


# ── Customers ─────────────────────────────────────────────────────────────────

def get_customers():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM customers ORDER BY name").fetchall()]

def add_customer(name, phone, email):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO customers (name,phone,email) VALUES (?,?,?)",
            (name, phone or None, email or None)
        )
        conn.commit()

def delete_customer(cid):
    with get_conn() as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (cid,))
        conn.commit()

def search_customer_by_phone(phone):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()
    return dict(row) if row else None


# ── Discounts ─────────────────────────────────────────────────────────────────

def get_discounts():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM discounts").fetchall()]

def get_discount_by_code(code):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM discounts WHERE code=? AND active=1", (code,)
        ).fetchone()
    return dict(row) if row else None

def add_discount(code, percentage):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO discounts (code,percentage) VALUES (?,?)",
            (code, percentage)
        )
        conn.commit()

def update_discount(did, code, percentage, active):
    with get_conn() as conn:
        conn.execute(
            "UPDATE discounts SET code=?,percentage=?,active=? WHERE id=?",
            (code, percentage, active, did)
        )
        conn.commit()

def delete_discount(did):
    with get_conn() as conn:
        conn.execute("DELETE FROM discounts WHERE id=?", (did,))
        conn.commit()


# ── Orders ────────────────────────────────────────────────────────────────────

def place_order(table_id, customer_id, cashier, discount_id, subtotal, discount_amount, total, items):
    """items: list of dicts with menu_item_id, name, price, quantity"""
    with get_conn() as conn:
        try:
            cur = conn.execute(
                """INSERT INTO orders
                   (table_id,customer_id,cashier,discount_id,subtotal,discount_amount,total)
                   VALUES (?,?,?,?,?,?,?)""",
                (table_id, customer_id, cashier, discount_id, subtotal, discount_amount, total)
            )
            order_id = cur.lastrowid
            for item in items:
                conn.execute(
                    """INSERT INTO order_items (order_id,menu_item_id,name,price,quantity)
                       VALUES (?,?,?,?,?)""",
                    (order_id, item["menu_item_id"], item["name"], item["price"], item["quantity"])
                )
            if table_id:
                conn.execute("UPDATE tables SET status='free' WHERE id=?", (table_id,))
            conn.commit()
            return order_id
        except Exception:
            conn.rollback()
            raise


# ── Reports ───────────────────────────────────────────────────────────────────

def get_sales_report(date_from, date_to):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT o.id, o.created_at, o.cashier, o.subtotal,
                   o.discount_amount, o.total, t.number as table_number,
                   c.name as customer_name
            FROM orders o
            LEFT JOIN tables t ON o.table_id = t.id
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE DATE(o.created_at) BETWEEN ? AND ?
              AND o.status = 'paid'
            ORDER BY o.created_at DESC
        """, (date_from, date_to)).fetchall()
        return [dict(r) for r in rows]

def get_report_summary(date_from, date_to):
    with get_conn() as conn:
        row = conn.execute("""
            SELECT COUNT(*) as total_orders,
                   COALESCE(SUM(subtotal),0) as gross,
                   COALESCE(SUM(discount_amount),0) as discounts,
                   COALESCE(SUM(total),0) as net
            FROM orders
            WHERE DATE(created_at) BETWEEN ? AND ?
              AND status='paid'
        """, (date_from, date_to)).fetchone()
        return dict(row)

def get_top_items(date_from, date_to, limit=10):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT oi.name, SUM(oi.quantity) as qty, SUM(oi.price*oi.quantity) as revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE DATE(o.created_at) BETWEEN ? AND ?
              AND o.status='paid'
            GROUP BY oi.name
            ORDER BY qty DESC
            LIMIT ?
        """, (date_from, date_to, limit)).fetchall()
        return [dict(r) for r in rows]
