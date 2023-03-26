import sqlite3
from database import SUBSCRIPTIONS_DB, create_connection

def get_subscription_stats(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, is_active FROM subscriptions")
    all_subscriptions = cursor.fetchall()

    active_subscriptions = [sub for sub in all_subscriptions if sub[1] == 1]
    user_subscriptions = [sub for sub in all_subscriptions if sub[0] > 0]
    group_subscriptions = [sub for sub in all_subscriptions if sub[0] < 0]

    active_user_subscriptions = [sub for sub in active_subscriptions if sub[0] > 0]
    active_group_subscriptions = [sub for sub in active_subscriptions if sub[0] < 0]

    return {
        "total": len(all_subscriptions),
        "active": len(active_subscriptions),
        "users": len(user_subscriptions),
        "groups": len(group_subscriptions),
        "active_users": len(active_user_subscriptions),
        "active_groups": len(active_group_subscriptions),
    }

def pretty_print_stats(stats):
    print("Total Subscriptions: ", stats["total"])
    print("Active Subscriptions: ", stats["active"])
    print("User Subscriptions: ", stats["users"])
    print("Group Subscriptions: ", stats["groups"])
    print("Active User Subscriptions: ", stats["active_users"])
    print("Active Group Subscriptions: ", stats["active_groups"])

def main():
    conn = create_connection(SUBSCRIPTIONS_DB)
    stats = get_subscription_stats(conn)
    pretty_print_stats(stats)

if __name__ == "__main__":
    main()
