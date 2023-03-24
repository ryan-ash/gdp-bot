from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN, ADMIN_CHAT_ID
import pytz

from handlers.command_handlers import register_command_handlers
from handlers.callback_handlers import register_callback_handlers
from utils.scheduler import schedule_trigger
from database import create_connection, create_subscriptions_table, create_posts_table, SUBSCRIPTIONS_DB, POSTS_DB

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

register_command_handlers(dp)
register_callback_handlers(dp)

async def on_startup(dp):
    subs_conn = create_connection(SUBSCRIPTIONS_DB)
    create_subscriptions_table(subs_conn)

    posts_conn = create_connection(POSTS_DB)
    create_posts_table(posts_conn)

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
