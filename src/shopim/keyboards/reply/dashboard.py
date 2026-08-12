from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DashboardCallback(CallbackData, prefix="dash"):
    action: str  # refresh


def get_dashboard_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔄 Yangilash",
        callback_data=DashboardCallback(action="refresh").pack(),
    )
    return builder.as_markup()