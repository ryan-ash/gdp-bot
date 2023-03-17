from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Message
from croniter import croniter
from cron_descriptor import get_description
from database import *
from states import BotStates
from typing import Optional
from utils.menu import show_menu


async def gdp_sub(message: Message, state: Optional[FSMContext] = None):
    chat_id = message.chat.id
    conn = create_connection()
    subscription = get_subscription(conn, chat_id)

    if subscription is None:
        subscribe(conn, chat_id)
        response = "You have been successfully subscribed!"
    elif subscription['is_active'] == 0:
        update_subscription_status(conn, chat_id, 1)
        response = "You have been successfully subscribed!"
    else:
        response = "You are already subscribed!"

    conn.close()
    return response


async def gdp_unsub(message: Message, state: Optional[FSMContext] = None):
    chat_id = message.chat.id
    conn = create_connection()
    unsubscribe(conn, chat_id)
    conn.close()
    return "You have successfully unsubscribed."


async def gdp_schedule(message: Message, state: Optional[FSMContext] = None):
    await message.reply(
        "Please enter the scheduling rules in cron format. For help, use this link: [Crontab Guru](https://crontab.guru/)",
        parse_mode=ParseMode.MARKDOWN,
    )
    await BotStates.waiting_for_schedule.set()


async def gdp_filter(message: Message, state: Optional[FSMContext] = None):
    await message.reply("Please enter the filter:")
    await BotStates.waiting_for_filter.set()


async def show_about(message: Message):
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
    async def start_command(message: Message):
        about_text = await show_about(message)
        await show_menu(message, about_text)

    @dp.message_handler(Command("gdp_sub"), state="*")
    async def gdp_subscribe_command(message: Message, state: FSMContext):
        await BotStates.waiting_for_subscribe.set()
        response = await gdp_sub(message)
        await show_menu(message, text=response)

    @dp.message_handler(Command("gdp_unsub"), state="*")
    async def gdp_unsubscribe_command(message: Message, state: FSMContext):
        await BotStates.waiting_for_unsubscribe.set()
        response = await gdp_unsub(message)
        await show_menu(message, text=response)

    @dp.message_handler(Command("gdp_schedule"), state="*")
    async def gdp_schedule_command(message: Message, state: FSMContext):
        await gdp_schedule(message, state)

    @dp.message_handler(lambda message: not message.text.startswith("/"), state=BotStates.waiting_for_schedule)
    async def process_schedule(message: Message, state: FSMContext):
        await schedule_step(message, state)

    @dp.message_handler(Command("gdp_filter"), state="*")
    async def gdp_filter_command(message: Message, state: FSMContext):
        await gdp_filter(message, state)

    @dp.message_handler(lambda message: not message.text.startswith("/"), state=BotStates.waiting_for_filter)
    async def process_filter(message: Message, state: FSMContext):
        # Save the filter
        conn = create_connection()
        chat_id = message.chat.id
        filter_text = message.text.strip()

        if not filter_text:
            response = "Filter is off, all materials will be considered."
        else:
            response = f"The filter has been updated successfully. New filter: {filter_text}"

        # Finish the FSM
        await state.finish()
        await show_menu(message, response)

    @dp.message_handler(Command("cancel"), state=BotStates.waiting_for_schedule)
    async def cancel_schedule_command(message: Message, state: FSMContext):
        response = "Scheduling process cancelled."
        await state.finish()
        await show_menu(message, response)

async def schedule_step(message: Message, state: FSMContext):
    cron_string = message.text

    if croniter.is_valid(cron_string):
        conn = create_connection()
        chat_id = message.chat.id
        update_subscription_schedule(conn, chat_id, cron_string)
        conn.close()

        human_readable_cron = get_description(cron_string)
        response = f"Schedule has been set successfully. New schedule: {human_readable_cron}"
        await state.finish()
        await show_menu(message, response)
    else:
        await message.reply("Invalid cron format. Please enter a valid cron format or type /cancel to exit.")
