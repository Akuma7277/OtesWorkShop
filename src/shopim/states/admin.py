from aiogram.fsm.state import State, StatesGroup

class UserRejectionState(StatesGroup):
    getting_reason = State()

class OrderRejectionState(StatesGroup):
    getting_reason = State()

class StockAdjustmentState(StatesGroup):
    getting_grams = State()
    getting_reason = State()


class ProductCreationState(StatesGroup):
    getting_name = State()
    getting_category = State()
    getting_description = State()
    getting_image = State()
    getting_cost_price = State()
    getting_sale_price = State()
    getting_initial_stock = State()
    getting_low_stock_threshold = State()


class ProductEditingState(StatesGroup):
    choosing_field = State()
    getting_name = State()
    getting_description = State()
    getting_image = State()
    getting_cost_price = State()
    getting_sale_price = State()
    getting_low_stock_threshold = State()


class TopupRejectionState(StatesGroup):
    getting_reason = State()


class UserManagementState(StatesGroup):
    getting_search_query = State()
    viewing_user = State()
    getting_balance_amount = State()
    getting_balance_reason = State()

class OrderBrowsingState(StatesGroup):
    getting_search_query = State()

class SettingsManagementState(StatesGroup):
    choosing_setting = State()
    getting_new_value = State()
