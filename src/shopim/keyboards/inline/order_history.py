from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Order


class OrderHistoryPageCallback(CallbackData, prefix="order_hist_page"):
    page: int


class ViewOrderCallback(CallbackData, prefix="view_order"):
    order_id: int
    page: int = 1


def get_order_history_keyboard(
    orders: Sequence[Order], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(
            text=f"№{order.order_number} - {order.total_amount:.2f} so'm",
            callback_data=ViewOrderCallback(order_id=order.id, page=current_page).pack(),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data=OrderHistoryPageCallback(page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Oldinga",
                callback_data=OrderHistoryPageCallback(page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()


def get_order_detail_keyboard(page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Buyurtmalar ro'yxatiga",
        callback_data=OrderHistoryPageCallback(page=page).pack(),
    )
    return builder.as_markup()
