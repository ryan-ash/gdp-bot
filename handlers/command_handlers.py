from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Message
from database import *
from utils.menu import show_menu
from states import BotStates
from croniter import croniter



async def gdp_sub(message: Message):
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


async def gdp_unsub(message: Message):
    chat_id = message.chat.id
    conn = create_connection()
    unsubscribe(conn, chat_id)
    conn.close()
    return "You have successfully unsubscribed."

async def gdp_schedule(message: Message):
    # Your gdp_schedule function
    pass

async def gdp_filter(message: Message):
    # Your gdp_filter function
    pass

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
        await message.reply(
            "Please enter the scheduling rules in cron format. For help, use this link: [Crontab Guru](https://crontab.guru/)",
            parse_mode=ParseMode.MARKDOWN,
        )
        await BotStates.waiting_for_schedule.set()

    @dp.message_handler(lambda message: not message.text.startswith("/"), state=BotStates.waiting_for_schedule)
    async def process_schedule(message: Message, state: FSMContext):
        await schedule_step(message, state)

    @dp.message_handler(Command("gdp_filter"), state="*")
    async def gdp_filter_command(message: Message, state: FSMContext):
        await message.reply("Please enter the filter:")
        await BotStates.waiting_for_filter.set()

    @dp.message_handler(lambda message: not message.text.startswith("/"), state=BotStates.waiting_for_filter)
    async def process_filter(message: Message, state: FSMContext):
        # Save the filter
        conn = create_connection()
        chat_id = message.chat.id
        update_subscription_filter(conn, chat_id, message.text)
        conn.close()

        # Send a success message
        await message.reply("The filter has been updated successfully. New filter: " + message.text)

        # Show the menu
        await show_menu(message)

        # Finish the FSM
        await state.finish()

    @dp.message_handler(Command("cancel"), state=BotStates.waiting_for_schedule)
    async def cancel_schedule_command(message: Message, state: FSMContext):
        await message.reply("Scheduling process cancelled.")
        await state.finish()


async def handle_gdp_filter(message: Message):
    # Add your filter handling logic here
    return "Filter handling logic goes here."

async def handle_gdp_schedule(message: Message):
    # Add your schedule handling logic here
    return "Schedule handling logic goes here."

async def schedule_step(message: Message, state: FSMContext):
    cron_string = message.text

    if croniter.is_valid(cron_string):
        conn = create_connection()
        chat_id = message.chat.id
        update_subscription_schedule(conn, chat_id, cron_string)
        conn.close()

        await message.reply("The schedule has been updated successfully. New schedule: " + cron_string)
        await state.finish()
    else:
        await message.reply("Invalid cron format. Please enter a valid cron format or type /cancel to exit.")
