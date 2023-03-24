import sqlite3
from config import IGNORED_POSTS
from sqlite3 import Error

SUBSCRIPTIONS_DB = 'subscriptions.db'
POSTS_DB = 'posts.db'


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def create_subscriptions_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER UNIQUE,
                        is_active INTEGER,
                        filter TEXT,
                        schedule TEXT
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS meta (
                        key TEXT PRIMARY KEY,
                        value TEXT
                     )''')
    

def create_posts_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY,
                        content TEXT NOT NULL
                     )''')


def clear_posts_table(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts")
    conn.commit()


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


def get_subscriptions(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM subscriptions WHERE is_active = 1 AND schedule IS NOT NULL")
    rows = cur.fetchall()
    return rows


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


def add_post(conn, post_id, content):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO posts (id, content) VALUES (?, ?)", (post_id, content))
    conn.commit()


def get_last_post_handled(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM meta WHERE key='last_post_handled'")
    result = cursor.fetchone()
    return int(result[0]) if result else None


def update_last_post_handled(conn, post_id):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_post_handled', ?)", (str(post_id),))
    conn.commit()


def get_all_posts(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()

    posts = []
    for row in rows:
        post = {
            "id": row[0],
            "content": row[1]
        }
        posts.append(post)
    return posts


def get_filtered_posts(conn, filter_list):
    cur = conn.cursor()
    query = "SELECT * FROM posts WHERE id NOT IN ({}) AND TRIM(content) <> ''".format(",".join(map(str, IGNORED_POSTS)))
    
    if filter_list:
        query += " AND ("
        query += " OR ".join([f"content LIKE '%{filter_}%' " for filter_ in filter_list])
        query += ")"
    
    cur.execute(query)
    rows = cur.fetchall()
    return rows


def count_posts(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    return cursor.fetchone()[0]


def search_post_with_string(conn, search_string):
    query = "SELECT * FROM posts WHERE content LIKE ?"
    cursor = conn.cursor()
    cursor.execute(query, (f"%{search_string}%",))
    return cursor.fetchone()
