from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Order


class OrderBrowseCallback(CallbackData, prefix="order_browse"):
    action: str  # search, page, select
    order_id: int | None = None
    page: int = 1


def get_order_browsing_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("🔍 Buyurtma qidirish"),
        callback_data=OrderBrowseCallback(action="search").pack(),
    )
    return builder.as_markup()


def get_order_search_results_keyboard(
    orders: Sequence[Order], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for order in orders:
        text = f"№{order.order_number} - {order.user.full_name} ({order.total_amount:.2f} {_('so\'m')})"
        builder.button(
            text=text,
            callback_data=OrderBrowseCallback(
                action="select", order_id=order.id, page=current_page
            ).pack(),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=OrderBrowseCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=OrderBrowseCallback(action="page", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text=_("⤴️ Yangi qidiruv"),
            callback_data=OrderBrowseCallback(action="search").pack(),
        )
    )
    return builder.as_markup()
