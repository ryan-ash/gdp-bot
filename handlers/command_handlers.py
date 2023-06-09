from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Message, CallbackQuery
from config import CHANNEL_USERNAME, RECOMMENDED_FILTERS, ABOUT_COVER_URL, ABOUT_COVER_AMOUNT
from croniter import croniter
from cron_descriptor import ExpressionDescriptor
from database import *
from states import BotStates
from typing import Optional
from utils.menu import show_menu
from utils.scheduler import fetch_and_send_post
import random
import time


def get_random_about_cover_url():
    if ABOUT_COVER_AMOUNT == 1:
        return ABOUT_COVER_URL
    else:
        random_number = random.randint(1, ABOUT_COVER_AMOUNT)
        return ABOUT_COVER_URL.replace('{index}', str(random_number))


async def get_subscription_info(chat_id):
    conn = create_connection(SUBSCRIPTIONS_DB)
    subscription = get_subscription(conn, chat_id)

    if not subscription or not subscription["is_active"]:
        filter_data = subscription['filter'] if subscription and subscription['filter'] else "-"
        return f"You are not currently subscribed.\n\nFilter: {filter_data}"

    filter_data = subscription['filter'] if subscription['filter'] else "-"
    if subscription['schedule']:
        schedule = ExpressionDescriptor(subscription['schedule']).get_description()
    else:
        schedule = "Not set"

    return f"You are currently subscribed with the following preferences:\n\nFilter: {filter_data}\nSchedule: {schedule}"


async def is_valid_sender(bot, chat_id, user_id):
    if chat_id > 0:  # private chat
        return True
    elif chat_id < 0:  # group or supergroup
        user = await bot.get_chat_member(chat_id, user_id)
        return user.is_chat_admin() or user.is_chat_creator()
    return False


async def is_valid_sender_and_reply(obj):
    if isinstance(obj, Message):
        message = obj
    elif isinstance(obj, CallbackQuery):
        message = obj.message
    else:
        raise ValueError("Invalid input type. Expected Message or CallbackQuery.")

    chat_id = message.chat.id
    user_id = obj.from_user.id
    bot = message.bot

    if await is_valid_sender(bot, chat_id, user_id):
        return True
    else:
        if isinstance(obj, Message):
            await obj.reply("You do not have the required permissions.")
        elif isinstance(obj, CallbackQuery):
            await obj.answer("You do not have the required permissions.")
        return False


async def gdp_sub(message: Message, state: Optional[FSMContext] = None):
    chat_id = message.chat.id
    conn = create_connection(SUBSCRIPTIONS_DB)
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
    conn = create_connection(SUBSCRIPTIONS_DB)
    unsubscribe(conn, chat_id)
    conn.close()
    return "You have successfully unsubscribed."


async def gdp_schedule(message: Message, state: Optional[FSMContext] = None):
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    offset_hours = int(offset / -3600)
    server_timezone = f"UTC{offset_hours:+d}"
    additional_prompt = ""

    additional_prompt = "\n\nType /cancel to exit."
    if message.chat.type != "private":
        additional_prompt += "\nReply to this message to update the value."

    await message.reply(
        f"Please enter the scheduling rules in cron format. For help, use this link: [Crontab Guru](https://crontab.guru/)\n\n"
        f"Server timezone: {server_timezone}"
        f"{additional_prompt}",
        parse_mode=ParseMode.MARKDOWN,
    )
    await BotStates.waiting_for_schedule.set()


async def gdp_filter(message: Message, state: Optional[FSMContext] = None):
    chat_id = message.chat.id
    conn = create_connection(SUBSCRIPTIONS_DB)
    subscription = get_subscription(conn, chat_id)
    current_filter = subscription['filter'] if subscription and subscription['filter'] else '-'

    additional_prompt = "\n\nType /cancel to exit."
    if message.chat.type != "private":
        additional_prompt += "\nReply to this message to update the value."

    prompt = f"Enter the filter using | to separate multiple filters, or * for no filter.\n\nRecommended: <code>{RECOMMENDED_FILTERS}</code>\nCurrent: <code>{current_filter}</code>{additional_prompt}"

    await message.reply(prompt, parse_mode='HTML')
    await BotStates.waiting_for_filter.set()


async def show_about(message: Message):
    chat_id = message.chat.id
    subscription_info = await get_subscription_info(chat_id)

    about_cover_url = get_random_about_cover_url()
    invisible_link = f'<a href="{about_cover_url}">&#8203;</a>'

    about_text = (
        invisible_link +
        f"Hey there! This rad bot hooks you up with updates from the {CHANNEL_USERNAME} channel, tailored just for you!"
        "Subscribe and customize your schedule and filters, so you'll only get the coolest, most wicked posts that suit your taste. Rock on!"
    )
    
    if subscription_info:
        about_text += f"\n\n{subscription_info}"

    about_text += (
        "\n\nCommands:"
        "\n- /gdp_sub: Subscribe"
        "\n- /gdp_unsub: Unsubscribe"
        "\n- /gdp_schedule: Set schedule"
        "\n- /gdp_filter: Set filters"
        "\n- /gdp_fetch: Fetch a post according to your filter"
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
        if await is_valid_sender_and_reply(message):
            await BotStates.waiting_for_subscribe.set()
            response = await gdp_sub(message)
            await show_menu(message, text=response)


    @dp.message_handler(Command("gdp_unsub"), state="*")
    async def gdp_unsubscribe_command(message: Message, state: FSMContext):
        if await is_valid_sender_and_reply(message):
            await BotStates.waiting_for_unsubscribe.set()
            response = await gdp_unsub(message)
            await show_menu(message, text=response)


    @dp.message_handler(Command("gdp_schedule"), state="*")
    async def gdp_schedule_command(message: Message, state: FSMContext):
        if await is_valid_sender_and_reply(message):
            await gdp_schedule(message, state)


    @dp.message_handler(lambda message: not message.text.startswith("/"), state=BotStates.waiting_for_schedule)
    async def process_schedule(message: Message, state: FSMContext):
        if await is_valid_sender_and_reply(message):
            await schedule_step(message, state)


    @dp.message_handler(Command("gdp_filter"), state="*")
    async def gdp_filter_command(message: Message, state: FSMContext):
        if await is_valid_sender_and_reply(message):
            await gdp_filter(message, state)


    @dp.message_handler(lambda message: not message.text.startswith("/"), state=BotStates.waiting_for_filter)
    async def process_filter(message: Message, state: FSMContext):
        if await is_valid_sender_and_reply(message):
            conn = create_connection(SUBSCRIPTIONS_DB)
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
    async def cancel_command(message: Message, state: FSMContext):
        if await is_valid_sender_and_reply(message):
            response = "You've changed your mind, and the settings will remain the same."
            subscription_info = await get_subscription_info(message.chat.id)
            response = f"{response}\n\n{subscription_info}"
            await state.finish()
            await show_menu(message, response)


    @dp.message_handler(Command("gdp_fetch"), state="*")
    async def gdp_fetch_command(message: Message, state: FSMContext):
        await send_filtered_post(message, state)


async def schedule_step(message: Message, state: FSMContext):
    cron_string = message.text

    if croniter.is_valid(cron_string):
        conn = create_connection(SUBSCRIPTIONS_DB)
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


async def send_filtered_post(message: Message, state: FSMContext):
    bot = message.bot
    chat_id = message.chat.id
    conn = create_connection(SUBSCRIPTIONS_DB)
    subscription = get_subscription(conn, chat_id)

    if subscription is None:
        subscribe(conn, chat_id)
        unsubscribe(conn, chat_id)
        subscription = get_subscription(conn, chat_id)

    fetched_and_sent = await fetch_and_send_post(bot, chat_id, subscription['filter'])
    if not fetched_and_sent:
        response = "No posts found matching your filter preferences."
        await message.reply(response)
