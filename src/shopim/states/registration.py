from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    choosing_language = State()
    getting_full_name = State()
    getting_phone_number = State()
    getting_address = State()
    getting_age = State()
    accepting_rules = State()
