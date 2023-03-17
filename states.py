from aiogram.dispatcher.filters.state import State, StatesGroup

class BotStates(StatesGroup):
    waiting_for_schedule = State()
    waiting_for_filter = State()
    waiting_for_subscribe = State()
    waiting_for_unsubscribe = State()
