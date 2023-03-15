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
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                            chat_id INTEGER PRIMARY KEY,
                            is_subscribed INTEGER
                          );''')
    except Error as e:
        print(e)

def add_subscription(conn, chat_id):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscriptions (chat_id, is_subscribed) VALUES (?, ?)", (chat_id, 1))
        conn.commit()
    except Error as e:
        print(e)

def remove_subscription(conn, chat_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscriptions WHERE chat_id=?", (chat_id,))
        conn.commit()
    except Error as e:
        print(e)

def get_subscriptions(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM subscriptions WHERE is_subscribed=1")
    rows = cursor.fetchall()
    subscriptions = [row[0] for row in rows]
    return subscriptions
