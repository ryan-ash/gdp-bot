import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

TOKEN = os.environ.get('GDP_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('GDP_BOT_ADMIN_CHAT_ID')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

subscriptions = {}

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
    # set schedule for user or group
    pass

async def gdp_filter(message: types.Message):
    # set tag filters for user or group
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

async def show_menu(message: types.Message, text: str = "Select an option:"):
    chat_id = message.chat.id
    is_subscribed = chat_id in subscriptions

    keyboard = InlineKeyboardMarkup()

    if is_subscribed:
        button_unsub = InlineKeyboardButton(text='Unsubscribe', callback_data='unsub')
        button_set_filter = InlineKeyboardButton(text='Set Filter', callback_data='set_filter')
        button_set_schedule = InlineKeyboardButton(text='Set Schedule', callback_data='set_schedule')

        keyboard.add(button_unsub)
        keyboard.add(button_set_filter)
        keyboard.add(button_set_schedule)
    else:
        button_sub = InlineKeyboardButton(text='Subscribe', callback_data='sub')
        keyboard.add(button_sub)

    button_about = InlineKeyboardButton(text='About', callback_data='about')
    keyboard.add(button_about)

    await message.reply(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ['sub', 'unsub', 'set_filter', 'set_schedule', 'about'])
async def handle_callback(callback_query: types.CallbackQuery):
    option = callback_query.data
    chat_id = callback_query.message.chat.id

    if option == 'sub':
        response = await gdp_sub(callback_query.message)
    elif option == 'unsub':
        response = await gdp_unsub(callback_query.message)
    elif option == 'set_filter':
        response = await handle_gdp_filter(callback_query.message)
    elif option == 'set_schedule':
        response = await handle_gdp_schedule(callback_query.message)
    elif option == 'about':
        response = await show_about(callback_query.message)

    await show_menu(callback_query.message, response)
    await bot.answer_callback_query(callback_query.id)

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

async def on_startup(dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been started')

async def on_shutdown(dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been stopped')

    await dp.storage.close()
    await dp.storage.wait_closed()

    await bot.session.close()

async def schedule_trigger():
    # trigger on schedule for each user/group that subscribed for that time
    pass


if __name__ == '__main__':
    from aiogram import executor
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    scheduler.add_job(schedule_trigger, 'interval', minutes=1)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
