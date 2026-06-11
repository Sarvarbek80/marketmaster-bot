import sqlite3
import os
from datetime import datetime

DB_PATH = "bot.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            tg_id INTEGER UNIQUE,
            username TEXT,
            full_name TEXT,
            status TEXT DEFAULT 'new',
            selected_tarif TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            tarif TEXT,
            status TEXT DEFAULT 'pending',
            check_file_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            tg_id INTEGER,
            extra TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Default settings
    defaults = {
        "price_standart": "299000",
        "price_optimal": "449000",
        "price_vip": "999000",
        "slots_standart": "20",
        "slots_optimal": "8",
        "slots_vip": "3",
        "cohort_date": "Tez orada",
        "group_standart": "",
        "group_optimal": "",
        "group_vip": "",
        "card_number": "",
        "click_url": "",
        "payme_url": "",
    }
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()


# ── Settings ──────────────────────────────────────────────
def get_setting(key):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(key, value):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────────────────
def upsert_user(tg_id, username, full_name):
    conn = get_conn()
    conn.execute("""
        INSERT INTO users (tg_id, username, full_name)
        VALUES (?, ?, ?)
        ON CONFLICT(tg_id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name,
            last_active=CURRENT_TIMESTAMP
    """, (tg_id, username, full_name))
    conn.commit()
    conn.close()


def get_user(tg_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_status(tg_id, status):
    conn = get_conn()
    conn.execute("UPDATE users SET status=?, last_active=CURRENT_TIMESTAMP WHERE tg_id=?", (status, tg_id))
    conn.commit()
    conn.close()


def update_user_tarif(tg_id, tarif):
    conn = get_conn()
    conn.execute("UPDATE users SET selected_tarif=? WHERE tg_id=?", (tarif, tg_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_users_by_status(status):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users WHERE status=?", (status,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_inactive_users(minutes):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM users
        WHERE status NOT IN ('student','reminded_24h')
        AND (strftime('%s','now') - strftime('%s', last_active)) > ?
    """, (minutes * 60,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Orders ─────────────────────────────────────────────────
def create_order(tg_id, tarif):
    conn = get_conn()
    conn.execute("""
        INSERT INTO orders (tg_id, tarif) VALUES (?, ?)
    """, (tg_id, tarif))
    conn.commit()
    conn.close()


def update_order_check(tg_id, file_id):
    conn = get_conn()
    conn.execute("""
        UPDATE orders SET check_file_id=?, status='check_sent', updated_at=CURRENT_TIMESTAMP
        WHERE tg_id=? AND status='pending'
    """, (file_id, tg_id))
    conn.commit()
    conn.close()


def get_pending_orders():
    conn = get_conn()
    rows = conn.execute("""
        SELECT o.*, u.username, u.full_name
        FROM orders o JOIN users u ON o.tg_id=u.tg_id
        WHERE o.status='check_sent'
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order_by_id(order_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT o.*, u.username, u.full_name
        FROM orders o JOIN users u ON o.tg_id=u.tg_id
        WHERE o.id=?
    """, (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def approve_order(order_id):
    conn = get_conn()
    conn.execute("""
        UPDATE orders SET status='approved', updated_at=CURRENT_TIMESTAMP WHERE id=?
    """, (order_id,))
    conn.commit()
    conn.close()


def reject_order(order_id):
    conn = get_conn()
    conn.execute("""
        UPDATE orders SET status='rejected', updated_at=CURRENT_TIMESTAMP WHERE id=?
    """, (order_id,))
    conn.commit()
    conn.close()


def get_orders_filtered(period="all"):
    conn = get_conn()
    if period == "today":
        rows = conn.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
            WHERE date(o.created_at)=date('now')
        """).fetchall()
    elif period == "week":
        rows = conn.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
            WHERE o.created_at >= datetime('now','-7 days')
        """).fetchall()
    elif period == "month":
        rows = conn.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
            WHERE o.created_at >= datetime('now','-30 days')
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Statistics ─────────────────────────────────────────────
def log_event(event, tg_id=None, extra=None):
    conn = get_conn()
    conn.execute("INSERT INTO statistics (event, tg_id, extra) VALUES (?, ?, ?)", (event, tg_id, extra))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_conn()
    today_starts = conn.execute(
        "SELECT COUNT(*) as c FROM statistics WHERE event='start' AND date(created_at)=date('now')"
    ).fetchone()["c"]

    total_leads = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE status NOT IN ('new')"
    ).fetchone()["c"]

    total_payments = conn.execute(
        "SELECT COUNT(*) as c FROM orders WHERE status='approved'"
    ).fetchone()["c"]

    total_students = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE status='student'"
    ).fetchone()["c"]

    total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]

    popular_tarif = conn.execute("""
        SELECT tarif, COUNT(*) as c FROM orders WHERE status='approved'
        GROUP BY tarif ORDER BY c DESC LIMIT 1
    """).fetchone()

    conn.close()

    conversion = round((total_payments / total_users * 100), 1) if total_users > 0 else 0

    return {
        "today_starts": today_starts,
        "total_leads": total_leads,
        "total_payments": total_payments,
        "total_students": total_students,
        "total_users": total_users,
        "conversion": conversion,
        "popular_tarif": popular_tarif["tarif"] if popular_tarif else "—",
    }
