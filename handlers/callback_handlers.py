from aiogram import types
from aiogram.dispatcher import Dispatcher

from handlers.command_handlers import gdp_sub, gdp_unsub, handle_gdp_filter, handle_gdp_schedule, show_about
from utils.menu import show_menu

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
    await callback_query.bot.answer_callback_query(callback_query.id)

def register_callback_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_callback, lambda c: c.data in ['sub', 'unsub', 'set_filter', 'set_schedule', 'about'])