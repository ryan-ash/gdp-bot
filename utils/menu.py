from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database import create_connection, get_active_subscription, SUBSCRIPTIONS_DB

async def show_menu(message: Message, text: str = "Select an option:"):
    chat_id = message.chat.id
    conn = create_connection(SUBSCRIPTIONS_DB)
    subscription = get_active_subscription(conn, chat_id)
    conn.close()
    is_subscribed = subscription is not None

    keyboard = InlineKeyboardMarkup()

    button_set_filter = InlineKeyboardButton(text='Set Filter', callback_data='set_filter')
    button_fetch = InlineKeyboardButton(text='Fetch', callback_data='fetch')

    if is_subscribed:
        button_unsub = InlineKeyboardButton(text='Unsubscribe', callback_data='unsub')
        button_set_schedule = InlineKeyboardButton(text='Set Schedule', callback_data='set_schedule')
        keyboard.row(button_unsub, button_set_filter, button_set_schedule, button_fetch)
    else:
        button_sub = InlineKeyboardButton(text='Subscribe', callback_data='sub')
        keyboard.row(button_sub, button_set_filter, button_fetch)

    button_about = InlineKeyboardButton(text='About', callback_data='about')
    keyboard.add(button_about)

    await message.reply(text, reply_markup=keyboard, parse_mode='HTML')

