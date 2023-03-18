from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Message
from croniter import croniter
from cron_descriptor import get_description, ExpressionDescriptor
from database import *
from states import BotStates
from typing import Optional
from utils.menu import show_menu

async def get_subscription_info(chat_id):
    conn = create_connection()
    subscription = get_subscription(conn, chat_id)

    if not subscription or not subscription["is_active"]:
        return None

    filter_data = subscription['filter'] if subscription['filter'] else "-"
    if subscription['schedule']:
        schedule = ExpressionDescriptor(subscription['schedule']).get_description()
    else:
        schedule = "Not set"

    return f"You are currently subscribed with the following preferences:\n\nFilter: {filter_data}\nSchedule: {schedule}"

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

    subscription_info = await get_subscription_info(chat_id)
    response = f"{response}\n\n{subscription_info}"

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
        "Please enter the scheduling rules in cron format. For help, use this link: [Crontab Guru](https://crontab.guru/)\n\nType /cancel to exit.",
        parse_mode=ParseMode.MARKDOWN,
    )
    await BotStates.waiting_for_schedule.set()

async def gdp_filter(message: Message, state: Optional[FSMContext] = None):
    await message.reply("Please enter the filter (use | to separate multiple filters, * for no filter):\n\nType /cancel to exit.")
    await BotStates.waiting_for_filter.set()

async def show_about(message: Message):
    chat_id = message.chat.id
    subscription_info = await get_subscription_info(chat_id)

    about_text = (
        "This bot allows you to subscribe to receive updates from the @GameDevPorn channel according to your preferences.\n"
        "By subscribing, you can set a schedule and filters to receive a random post that matches your filters."
    )
    
    if subscription_info:
        about_text += f"\n\n{subscription_info}"

    about_text += (
        "\n\nCommands:"
        "\n- /gdp_sub: Subscribe"
        "\n- /gdp_unsub: Unsubscribe"
        "\n- /gdp_schedule: Set schedule"
        "\n- /gdp_filter: Set filters"
        "\n- /gdp_about: Show About information"
    )
    
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
        conn = create_connection()
        chat_id = message.chat.id
        filter_text = message.text.strip()

        if filter_text == "*":
            filter_text = ""

        update_subscription_filter(conn, chat_id, filter_text)
        conn.close()

        if not filter_text:
            response = "Filter is off, all materials will be considered."
        else:
            response = f"The filter has been updated successfully"

        subscription_info = await get_subscription_info(chat_id)
        response = f"{response}\n\n{subscription_info}"

        await state.finish()
        await show_menu(message, response)

    @dp.message_handler(Command("cancel"), state=[BotStates.waiting_for_schedule, BotStates.waiting_for_filter])
    async def cancel_schedule_command(message: Message, state: FSMContext):
        response = "You changed your mind and settings stay the same."
        subscription_info = await get_subscription_info(message.chat.id)
        response = f"{response}\n\n{subscription_info}"
        await state.finish()
        await show_menu(message, response)


async def schedule_step(message: Message, state: FSMContext):
    cron_string = message.text

    if croniter.is_valid(cron_string):
        conn = create_connection()
        chat_id = message.chat.id
        update_subscription_schedule(conn, chat_id, cron_string)
        conn.close()

        human_readable_cron = ExpressionDescriptor(cron_string).get_description()
        response = f"Schedule has been set successfully. New schedule: {human_readable_cron}"
        subscription_info = await get_subscription_info(chat_id)
        response = f"{response}\n\n{subscription_info}"

        await state.finish()
        await show_menu(message, response)
    else:
        await message.reply("Invalid cron format. Please enter a valid cron format or type /cancel to exit.")

