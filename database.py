import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('subscriptions.db')
        create_table(conn)  # Add this line
    except Error as e:
        print(e)
    return conn


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER UNIQUE,
                        is_active INTEGER,
                        filter TEXT,
                        schedule TEXT
                      )''')


def subscribe(conn, chat_id):
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO subscriptions (chat_id, is_active) VALUES (?, 1)
                      ON CONFLICT(chat_id) DO UPDATE SET is_active=1''', (chat_id,))
    conn.commit()


def unsubscribe(conn, chat_id):
    cursor = conn.cursor()
    cursor.execute('''UPDATE subscriptions SET is_active=0 WHERE chat_id=?''', (chat_id,))
    conn.commit()


def update_filter(conn, chat_id, filter_tags):
    cursor = conn.cursor()
    cursor.execute('''UPDATE subscriptions SET filter=? WHERE chat_id=?''', (filter_tags, chat_id))
    conn.commit()


def update_schedule(conn, chat_id, schedule):
    cursor = conn.cursor()
    cursor.execute('''UPDATE subscriptions SET schedule=? WHERE chat_id=?''', (schedule, chat_id))
    conn.commit()


def get_active_subscription(conn, chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE chat_id=? AND is_active=1", (chat_id,))
    return cursor.fetchone()


def get_subscription(conn, chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE chat_id=?", (chat_id,))
    row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "chat_id": row[1],
        "is_active": row[2],
        "filter": row[3],
        "schedule": row[4]
    }

def update_subscription_status(conn, chat_id, is_active):
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET is_active=? WHERE chat_id=?", (is_active, chat_id))
    conn.commit()

def update_subscription_filter(conn, chat_id, new_filter):
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET filter=? WHERE chat_id=?", (new_filter, chat_id))
    conn.commit()

def update_subscription_schedule(conn, chat_id, new_schedule):
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET schedule=? WHERE chat_id=?", (new_schedule, chat_id))
    conn.commit()
