from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class BalanceHistoryPageCallback(CallbackData, prefix="bal_page"):
    page: int


def get_balance_history_keyboard(
    total_pages: int, current_page: int
) -> InlineKeyboardMarkup | None:
    if total_pages <= 1:
        return None

    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data=BalanceHistoryPageCallback(page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Oldinga",
                callback_data=BalanceHistoryPageCallback(page=current_page + 1).pack(),
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()