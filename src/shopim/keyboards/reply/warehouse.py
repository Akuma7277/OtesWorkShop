from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Product


class WarehouseCallback(CallbackData, prefix="wh"):
    action: str  # menu, stock, movements, adjust_start, adjust_product_page
    page: int = 1

class ProductAdjustCallback(CallbackData, prefix="wh_adj"):
    action: str  # select
    product_id: int
    page: int  # for returning to the list

def get_warehouse_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📊 Qoldiqlar",
        callback_data=WarehouseCallback(action="stock", page=1),
    )
    builder.button(
        text="📜 Harakatlar tarixi",
        callback_data=WarehouseCallback(action="movements", page=1),
    )
    builder.button(
        text="✍️ Skladni tuzatish",
        callback_data=WarehouseCallback(action="adjust_start", page=1),
    )
    builder.adjust(2, 1)
    return builder.as_markup()


def get_product_selection_for_adjustment_keyboard(
    products: Sequence[Product], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} ({product.stock_grams} gr)",
            callback_data=ProductAdjustCallback(
                action="select", product_id=product.id, page=current_page
            ),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data=WarehouseCallback(
                    action="adjust_product_page", page=current_page - 1
                ).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Oldinga",
                callback_data=WarehouseCallback(
                    action="adjust_product_page", page=current_page + 1
                ).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⤴️ Sklad menyusiga",
            callback_data=WarehouseCallback(action="menu").pack(),
        )
    )
    return builder.as_markup()


def get_stock_balance_keyboard(
    total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data=WarehouseCallback(action="stock", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Oldinga",
                callback_data=WarehouseCallback(action="stock", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⤴️ Sklad menyusiga",
            callback_data=WarehouseCallback(action="menu").pack(),
        )
    )
    return builder.as_markup()


def get_stock_movements_keyboard(
    total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data=WarehouseCallback(
                    action="movements", page=current_page - 1
                ).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Oldinga",
                callback_data=WarehouseCallback(
                    action="movements", page=current_page + 1
                ).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⤴️ Sklad menyusiga",
            callback_data=WarehouseCallback(action="menu").pack(),
        )
    )
    return builder.as_markup()