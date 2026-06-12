import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tg_id BIGINT UNIQUE,
            username TEXT,
            full_name TEXT,
            status TEXT DEFAULT 'new',
            selected_tarif TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            tg_id BIGINT,
            tarif TEXT,
            status TEXT DEFAULT 'pending',
            check_file_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            id SERIAL PRIMARY KEY,
            event TEXT,
            tg_id BIGINT,
            extra TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        c.execute("""
            INSERT INTO settings (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO NOTHING
        """, (k, v))

    conn.commit()
    conn.close()


# ── Settings ──────────────────────────────────────────────
def get_setting(key):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=%s", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(key, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value) VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
    """, (key, value))
    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────────────────
def upsert_user(tg_id, username, full_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (tg_id, username, full_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (tg_id) DO UPDATE SET
            username=EXCLUDED.username,
            full_name=EXCLUDED.full_name,
            last_active=CURRENT_TIMESTAMP
    """, (tg_id, username, full_name))
    conn.commit()
    conn.close()


def get_user(tg_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE tg_id=%s", (tg_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_status(tg_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET status=%s, last_active=CURRENT_TIMESTAMP WHERE tg_id=%s", (status, tg_id))
    conn.commit()
    conn.close()


def update_user_tarif(tg_id, tarif):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET selected_tarif=%s WHERE tg_id=%s", (tarif, tg_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_users_by_status(status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE status=%s", (status,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_inactive_users(minutes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM users
        WHERE status NOT IN ('student', 'reminded_24h')
        AND EXTRACT(EPOCH FROM (NOW() - last_active)) > %s
    """, (minutes * 60,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Orders ─────────────────────────────────────────────────
def create_order(tg_id, tarif):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE tg_id=%s AND status='pending'", (tg_id,))
    c.execute("INSERT INTO orders (tg_id, tarif) VALUES (%s, %s)", (tg_id, tarif))
    conn.commit()
    conn.close()


def update_order_check(tg_id, file_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE orders SET check_file_id=%s, status='check_sent', updated_at=CURRENT_TIMESTAMP
        WHERE tg_id=%s AND status='pending'
    """, (file_id, tg_id))
    conn.commit()
    conn.close()


def get_pending_orders():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, u.username, u.full_name
        FROM orders o JOIN users u ON o.tg_id=u.tg_id
        WHERE o.status='check_sent'
        ORDER BY o.created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order_by_id(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, u.username, u.full_name
        FROM orders o JOIN users u ON o.tg_id=u.tg_id
        WHERE o.id=%s
    """, (order_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def approve_order(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE orders SET status='approved', updated_at=CURRENT_TIMESTAMP WHERE id=%s", (order_id,))
    conn.commit()
    conn.close()


def reject_order(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE orders SET status='rejected', updated_at=CURRENT_TIMESTAMP WHERE id=%s", (order_id,))
    conn.commit()
    conn.close()


def get_orders_filtered(period="all"):
    conn = get_conn()
    c = conn.cursor()
    if period == "today":
        c.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
            WHERE DATE(o.created_at)=CURRENT_DATE
        """)
    elif period == "week":
        c.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
            WHERE o.created_at >= NOW() - INTERVAL '7 days'
        """)
    elif period == "month":
        c.execute("""
            SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id
            WHERE o.created_at >= NOW() - INTERVAL '30 days'
        """)
    else:
        c.execute("SELECT o.*, u.username, u.full_name FROM orders o JOIN users u ON o.tg_id=u.tg_id")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Statistics ─────────────────────────────────────────────
def log_event(event, tg_id=None, extra=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO statistics (event, tg_id, extra) VALUES (%s, %s, %s)", (event, tg_id, extra))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) as c FROM statistics WHERE event='start' AND DATE(created_at)=CURRENT_DATE")
    today_starts = c.fetchone()["c"]

    c.execute("SELECT COUNT(*) as c FROM users WHERE status NOT IN ('new')")
    total_leads = c.fetchone()["c"]

    c.execute("SELECT COUNT(*) as c FROM orders WHERE status='approved'")
    total_payments = c.fetchone()["c"]

    c.execute("SELECT COUNT(*) as c FROM users WHERE status='student'")
    total_students = c.fetchone()["c"]

    c.execute("SELECT COUNT(*) as c FROM users")
    total_users = c.fetchone()["c"]

    c.execute("""
        SELECT tarif, COUNT(*) as c FROM orders WHERE status='approved'
        GROUP BY tarif ORDER BY c DESC LIMIT 1
    """)
    popular_tarif = c.fetchone()

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