import asyncio
from telethon import TelegramClient
from database import create_connection, add_post, get_last_post_handled, update_last_post_handled, count_posts
from config import API_ID, API_HASH, CHANNEL_LINK, PHONE

def display_posts(prefix):
    conn = create_connection()
    total_posts = count_posts(conn)
    print(f"{prefix} Total posts: {total_posts}")

async def sync_posts():
    conn = create_connection()
    last_post_handled = get_last_post_handled(conn)

    client = TelegramClient("anon", API_ID, API_HASH)
    await client.start(PHONE)

    channel = await client.get_entity(CHANNEL_LINK)
    
    print("Sync in progress...", end="", flush=True)

    counter = 0
    async for message in client.iter_messages(channel):
        if last_post_handled and message.id <= last_post_handled:
            break

        add_post(conn, message.id, message.text)
        update_last_post_handled(conn, message.id)
        counter += 1
        if counter % 10 == 0:
            print(".", end="", flush=True)

    print("\nSync completed.")
    await client.disconnect()

if __name__ == '__main__':
    display_posts("Before sync")
    asyncio.run(sync_posts())
    display_posts("After sync")
