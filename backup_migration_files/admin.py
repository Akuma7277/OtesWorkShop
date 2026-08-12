from aiogram.fsm.state import State, StatesGroup


class UserRejectionState(StatesGroup):
    getting_reason = State()


class OrderRejectionState(StatesGroup):
    getting_reason = State()