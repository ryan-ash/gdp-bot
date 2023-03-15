from aiogram import types
from state import subscriptions
from utils.menu import show_menu

async def gdp_sub(message: types.Message):
    chat_id = message.chat.id
    subscriptions[chat_id] = True
    return "You have successfully subscribed."

async def gdp_unsub(message: types.Message):
    chat_id = message.chat.id
    if chat_id in subscriptions:
        del subscriptions[chat_id]
        return "You have successfully unsubscribed."
    else:
        return "You are not currently subscribed."

async def gdp_schedule(message: types.Message):
    # Your gdp_schedule function
    pass

async def gdp_filter(message: types.Message):
    # Your gdp_filter function
    pass

async def show_about(message: types.Message):
    about_text = """
This bot allows you to subscribe to receive updates from the @GameDevPorn channel according to your preferences.
By subscribing, you can set a schedule and filters to receive a random post that matches your filters.
Commands:
- /gdp_sub: Subscribe
- /gdp_unsub: Unsubscribe
- /gdp_schedule: Set schedule
- /gdp_filter: Set filters
- /gdp_about: Show About information
"""
    return about_text

def register_command_handlers(dp):
    @dp.message_handler(commands=['start', 'gdp_about'])
    async def start_command(message: types.Message):
        about_text = await show_about(message)
        await show_menu(message, about_text)

    @dp.message_handler(commands=['gdp_sub'])
    async def handle_gdp_sub(message: types.Message):
        response = await gdp_sub(message)
        await show_menu(message, response)

    @dp.message_handler(commands=['gdp_unsub'])
    async def handle_gdp_unsub(message: types.Message):
        response = await gdp_unsub(message)
        await show_menu(message, response)

async def handle_gdp_filter(message: types.Message):
    # Add your filter handling logic here
    return "Filter handling logic goes here."

async def handle_gdp_schedule(message: types.Message):
    # Add your schedule handling logic here
    return "Schedule handling logic goes here."
