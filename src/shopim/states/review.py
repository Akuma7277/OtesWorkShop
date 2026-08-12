from aiogram.fsm.state import State, StatesGroup


class ReviewStates(StatesGroup):
    getting_text = State()
