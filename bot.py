import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

from handlers.command_handlers import register_command_handlers
from handlers.callback_handlers import register_callback_handlers
from utils.scheduler import schedule_trigger

TOKEN = os.environ.get('GDP_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('GDP_BOT_ADMIN_CHAT_ID')

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

register_command_handlers(dp)
register_callback_handlers(dp)

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
    scheduler.add_job(schedule_trigger, 'interval', minutes=1, args=(bot,))
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
