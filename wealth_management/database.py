import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "wealth.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                value REAL NOT NULL,
                currency TEXT DEFAULT 'BRL',
                institution TEXT,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline TEXT,
                category TEXT,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS asset_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                value REAL NOT NULL,
                recorded_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
            );
        """)


# ── Assets ──────────────────────────────────────────────────────────────────

def get_assets():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM assets ORDER BY category, name"
        ).fetchall()]


def add_asset(name, category, value, currency="BRL", institution="", notes=""):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO assets (name, category, value, currency, institution, notes) "
            "VALUES (?,?,?,?,?,?)",
            (name, category, value, currency, institution, notes),
        )
        asset_id = cur.lastrowid
        conn.execute(
            "INSERT INTO asset_history (asset_id, value) VALUES (?,?)",
            (asset_id, value),
        )
        return asset_id


def update_asset(asset_id, name, category, value, currency="BRL", institution="", notes=""):
    with get_connection() as conn:
        conn.execute(
            "UPDATE assets SET name=?, category=?, value=?, currency=?, institution=?, "
            "notes=?, updated_at=datetime('now') WHERE id=?",
            (name, category, value, currency, institution, notes, asset_id),
        )
        conn.execute(
            "INSERT INTO asset_history (asset_id, value) VALUES (?,?)",
            (asset_id, value),
        )


def delete_asset(asset_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM assets WHERE id=?", (asset_id,))


def get_asset_history(asset_id):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM asset_history WHERE asset_id=? ORDER BY recorded_at",
            (asset_id,),
        ).fetchall()]


# ── Transactions ─────────────────────────────────────────────────────────────

def get_transactions(limit=200, tx_type=None):
    sql = "SELECT * FROM transactions"
    params = []
    if tx_type:
        sql += " WHERE type=?"
        params.append(tx_type)
    sql += " ORDER BY date DESC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def add_transaction(tx_type, category, description, amount, date, notes=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO transactions (type, category, description, amount, date, notes) "
            "VALUES (?,?,?,?,?,?)",
            (tx_type, category, description, amount, date, notes),
        )


def delete_transaction(tx_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id=?", (tx_id,))


# ── Goals ─────────────────────────────────────────────────────────────────────

def get_goals():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM goals ORDER BY deadline"
        ).fetchall()]


def add_goal(name, target_amount, current_amount=0, deadline="", category="", notes=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO goals (name, target_amount, current_amount, deadline, category, notes) "
            "VALUES (?,?,?,?,?,?)",
            (name, target_amount, current_amount, deadline, category, notes),
        )


def update_goal(goal_id, name, target_amount, current_amount, deadline, category, notes):
    with get_connection() as conn:
        conn.execute(
            "UPDATE goals SET name=?, target_amount=?, current_amount=?, deadline=?, "
            "category=?, notes=? WHERE id=?",
            (name, target_amount, current_amount, deadline, category, notes, goal_id),
        )


def delete_goal(goal_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))


# ── Summary helpers ───────────────────────────────────────────────────────────

def get_net_worth():
    with get_connection() as conn:
        row = conn.execute("SELECT COALESCE(SUM(value),0) as total FROM assets").fetchone()
        return row["total"]


def get_monthly_summary(year, month):
    period = f"{year:04d}-{month:02d}"
    with get_connection() as conn:
        income = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM transactions "
            "WHERE type='income' AND date LIKE ?",
            (f"{period}%",),
        ).fetchone()["t"]
        expense = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM transactions "
            "WHERE type='expense' AND date LIKE ?",
            (f"{period}%",),
        ).fetchone()["t"]
        return income, expense


def get_assets_by_category():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT category, SUM(value) as total FROM assets GROUP BY category ORDER BY total DESC"
        ).fetchall()
        return [(r["category"], r["total"]) for r in rows]


def get_monthly_cashflow(months=6):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT strftime('%Y-%m', date) as month,
                   SUM(CASE WHEN type='income'  THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
            """,
            (months,),
        ).fetchall()
        return [(r["month"], r["income"], r["expense"]) for r in reversed(rows)]
