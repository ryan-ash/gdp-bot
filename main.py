import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

TOKEN = os.environ.get('GDP_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('GDP_BOT_ADMIN_CHAT_ID')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def gdp_sub(message: types.Message):
    # subscribe user or group
    pass

async def gdp_unsub(message: types.Message):
    # unsubscribe user or group
    pass

async def gdp_schedule(message: types.Message):
    # set schedule for user or group
    pass

async def gdp_filter(message: types.Message):
    # set tag filters for user or group
    pass

async def schedule_trigger():
    # trigger on schedule for each user/group that subscribed for that time
    pass

@dp.message_handler(commands=['gdp_sub'])
async def handle_gdp_sub(message: types.Message):
    await gdp_sub(message)

@dp.message_handler(commands=['gdp_unsub'])
async def handle_gdp_unsub(message: types.Message):
    await gdp_unsub(message)

@dp.message_handler(commands=['gdp_schedule'])
async def handle_gdp_schedule(message: types.Message):
    await gdp_schedule(message)

@dp.message_handler(commands=['gdp_filter'])
async def handle_gdp_filter(message: types.Message):
    await gdp_filter(message)

async def on_startup(dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been started')

async def on_shutdown(dp):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot has been stopped')

    await dp.storage.close()
    await dp.storage.wait_closed()

    await bot.session.close()

if __name__ == '__main__':
    from aiogram import executor
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    scheduler.add_job(schedule_trigger, 'interval', minutes=1)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
