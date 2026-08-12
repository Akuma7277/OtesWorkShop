from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DashboardCallback(CallbackData, prefix="dashboard"):
    action: str  # 'refresh', 'buyers', 'main_stats'


def get_dashboard_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("👥 Xaridorlar ro'yxati"),
        callback_data=DashboardCallback(action="buyers").pack(),
    )
    builder.button(
        text=_("🔄 Yangilash"),
        callback_data=DashboardCallback(action="refresh").pack(),
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def get_buyers_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("📊 Dashboard ga qaytish"),
        callback_data=DashboardCallback(action="main_stats").pack(),
    )
    builder.button(
        text=_("🔄 Yangilash"),
        callback_data=DashboardCallback(action="buyers").pack(),
    )
    builder.adjust(1, 1)
    return builder.as_markup()
