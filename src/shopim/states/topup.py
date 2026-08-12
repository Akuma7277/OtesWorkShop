from aiogram.fsm.state import State, StatesGroup


class TopupStates(StatesGroup):
    getting_amount = State()
    getting_receipt = State()
