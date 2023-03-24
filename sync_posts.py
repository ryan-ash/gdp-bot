from config import API_ID, API_HASH, CHANNEL_LINK, PHONE, SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASSWORD, SFTP_REMOTE_PATH
from database import create_connection, add_post, update_last_post_handled, count_posts, clear_posts_table, POSTS_DB, SUBSCRIPTIONS_DB
from telethon import TelegramClient
import asyncio
import os
import pysftp


def display_posts(prefix):
    conn = create_connection(POSTS_DB)
    total_posts = count_posts(conn)
    print(f"{prefix} Total posts: {total_posts}")


def sync_database_sftp(local_db_path):
    remote_db_path = os.path.join(SFTP_REMOTE_PATH, os.path.basename(local_db_path))

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(SFTP_HOST, username=SFTP_USER, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
        try:
            sftp.put(local_db_path, remote_db_path)
            print("SFTP sync completed successfully.")
        except Exception as e:
            print(f"Error: SFTP sync failed with error: {e}")


async def sync_posts():
    conn_posts = create_connection(POSTS_DB)
    conn_subs = create_connection(SUBSCRIPTIONS_DB)

    # Clear the posts table before starting the sync
    clear_posts_table(conn_posts)

    client = TelegramClient("anon", API_ID, API_HASH)
    await client.start(PHONE)

    channel = await client.get_entity(CHANNEL_LINK)
    
    print("Sync in progress...", end="", flush=True)

    counter = 0
    async for message in client.iter_messages(channel):
        add_post(conn_posts, message.id, message.text)
        update_last_post_handled(conn_subs, message.id)
        counter += 1
        if counter % 10 == 0:
            print(".", end="", flush=True)

    print("\nSync completed.")
    await client.disconnect()
    sync_database_sftp(POSTS_DB)


if __name__ == '__main__':
    display_posts("Before sync")
    asyncio.run(sync_posts())
    display_posts("After sync")
