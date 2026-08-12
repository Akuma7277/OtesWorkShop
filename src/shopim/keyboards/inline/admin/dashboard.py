from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DashboardCallback(CallbackData, prefix="dashboard"):
    action: str  # 'refresh'


def get_dashboard_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔄 Yangilash",
        callback_data=DashboardCallback(action="refresh").pack(),
    )
    return builder.as_markup()
