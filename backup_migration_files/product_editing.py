from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Product


class ProductEditCallback(CallbackData, prefix="prod_edit"):
    action: str  # select, page
    product_id: int | None = None
    page: int = 1


class ProductEditFieldCallback(CallbackData, prefix="prod_edit_field"):
    action: str  # choose_field, back_to_menu, toggle_active, delete_start, delete_confirm
    field: str | None = None  # name, description, price, etc.


def get_product_list_for_editing_keyboard(
    products: Sequence[Product], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=product.name,
            callback_data=ProductEditCallback(
                action="select", product_id=product.id, page=current_page
            ),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=ProductEditCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=ProductEditCallback(action="page", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()


def get_product_edit_menu_keyboard(product: Product, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = {
        "name": "Nomi",
        "description": "Tavsifi",
        "image": "Rasmi",
        "sale_price_per_gram": "Sotuv narxi",
        "cost_price_per_gram": "Tannarxi",
        "low_stock_threshold_grams": "Minimal qoldiq",
    }
    for field_key, field_name in fields.items():
        builder.button(
            text=f"✏️ {field_name}",
            callback_data=ProductEditFieldCallback(action="choose_field", field=field_key),
        )

    if product.is_active:
        builder.button(
            text="👁 Yashirish",
            callback_data=ProductEditFieldCallback(action="toggle_active"),
        )
    else:
        builder.button(
            text="👁 Ko'rsatish",
            callback_data=ProductEditFieldCallback(action="toggle_active"),
        )
    builder.button(
        text="🗑 O'chirish",
        callback_data=ProductEditFieldCallback(action="delete_start"),
    )

    builder.adjust(2, 2, 1)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Mahsulotlar ro'yxatiga",
            callback_data=ProductEditCallback(action="page", page=page).pack(),
        )
    )
    return builder.as_markup()


def get_back_to_edit_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Tahrirlash menyusiga",
        callback_data=ProductEditFieldCallback(action="back_to_menu").pack(),
    )
    return builder.as_markup()


def get_product_delete_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔴 Ha, o'chirish",
        callback_data=ProductEditFieldCallback(action="delete_confirm").pack(),
    )
    builder.button(
        text="⬅️ Bekor qilish",
        callback_data=ProductEditFieldCallback(action="back_to_menu").pack(),
    )
    return builder.as_markup()