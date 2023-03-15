from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from state import subscriptions

async def show_menu(message: Message, text: str = "Select an option:"):
    chat_id = message.chat.id
    is_subscribed = chat_id in subscriptions

    keyboard = InlineKeyboardMarkup()

    if is_subscribed:
        button_unsub = InlineKeyboardButton(text='Unsubscribe', callback_data='unsub')
        button_set_filter = InlineKeyboardButton(text='Set Filter', callback_data='set_filter')
        button_set_schedule = InlineKeyboardButton(text='Set Schedule', callback_data='set_schedule')

        keyboard.row(button_unsub, button_set_filter, button_set_schedule)
    else:
        button_sub = InlineKeyboardButton(text='Subscribe', callback_data='sub')
        keyboard.add(button_sub)

    button_about = InlineKeyboardButton(text='About', callback_data='about')
    keyboard.add(button_about)

    await message.reply(text, reply_markup=keyboard)
