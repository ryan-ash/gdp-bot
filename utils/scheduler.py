from config import ADMIN_CHAT_ID, CHANNEL_LINK
from database import create_connection, get_subscriptions, get_filtered_posts
from croniter import croniter
from datetime import datetime
import random

def is_time_to_send(schedule):
    now = datetime.now()
    cron = croniter(schedule, now)
    prev_time = cron.get_prev(datetime)
    next_time = cron.get_next(datetime)
    return prev_time < now < next_time

async def send_post_to_chat(bot, chat_id, post_id):
    post_link = f"{CHANNEL_LINK}/{post_id}"
    await bot.send_message(chat_id, post_link)

async def schedule_trigger(bot):
    conn = create_connection()
    subscriptions = get_subscriptions(conn)

    for subscription in subscriptions:
        chat_id = subscription[1]
        schedule = subscription[4]
        filters = subscription[3]

        if is_time_to_send(schedule):
            filter_list = filters.split('|')
            posts = get_filtered_posts(conn, filter_list)

            if posts:
                random_post = random.choice(posts)
                await send_post_to_chat(bot, chat_id, random_post[0])

async def on_startup(bot, dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been started')

async def on_shutdown(bot, dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been stopped')

    await dp.storage.close()
    await dp.storage.wait_closed()

    await bot.session.close()
