from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import quote_html
from config import ADMIN_CHAT_ID, CHANNEL_LINK
from database import create_connection, get_subscriptions, get_filtered_posts
from croniter import croniter
from datetime import datetime, timedelta
import random


def is_time_to_send(schedule):
    now = datetime.now()
    ref_time = now - timedelta(seconds=30)
    
    cron = croniter(schedule, ref_time)
    prev_time = cron.get_prev(datetime)
    next_time = cron.get_next(datetime)

    delta = next_time - prev_time
    tolerance = 60

    return abs((ref_time - prev_time).total_seconds() - delta.total_seconds()) <= tolerance


async def send_post_to_chat(bot, chat_id, post):
    post_id = post[0]
    post_text = post[1]
    post_link = f"{CHANNEL_LINK}/{post_id}"

    inline_button = InlineKeyboardButton("src", url=post_link)
    inline_kb = InlineKeyboardMarkup().add(inline_button)

    await bot.send_message(chat_id, post_text, reply_markup=inline_kb, parse_mode='Markdown')


async def schedule_trigger(bot):
    conn = create_connection()
    subscriptions = get_subscriptions(conn)

    for subscription in subscriptions:
        chat_id = subscription[1]
        schedule = subscription[4]
        filters = subscription[3]

        if is_time_to_send(schedule):
            filter_list = [] if filters is None else filters.split('|')
            posts = get_filtered_posts(conn, filter_list)

            if posts:
                random_post = random.choice(posts)
                await send_post_to_chat(bot, chat_id, random_post)


async def on_startup(bot, dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been started')

async def on_shutdown(bot, dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been stopped')

    await dp.storage.close()
    await dp.storage.wait_closed()

    await bot.session.close()
