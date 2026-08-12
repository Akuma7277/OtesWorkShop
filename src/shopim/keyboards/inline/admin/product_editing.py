from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Product


class ProductEditCallback(CallbackData, prefix="prod_edit"):
    action: str  # 'select', 'page', 'delete', 'confirm_delete', 'cancel_delete'
    product_id: int | None = None
    page: int = 1


class ProductEditFieldCallback(CallbackData, prefix="prod_edit_field"):
    field: str  # 'name', 'description', 'image', 'cost_price', 'sale_price', 'low_stock_threshold'
    product_id: int


def get_product_list_for_editing_keyboard(
    products: Sequence[Product], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} ({product.stock_grams} gr)",
            callback_data=ProductEditCallback(
                action="select", product_id=product.id, page=current_page
            ).pack(),
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


def get_product_edit_menu_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = [
        ("✏️ Nomini o'zgartirish", "name"),
        ("📝 Tavsifni o'zgartirish", "description"),
        ("🖼 Rasmni o'zgartirish", "image"),
        ("💰 Tannarxni o'zgartirish", "cost_price"),
        ("💵 Sotuv narxini o'zgartirish", "sale_price"),
        ("📉 Low stock chegarasini o'zgartirish", "low_stock_threshold"),
    ]
    for text, field in fields:
        builder.button(
            text=text,
            callback_data=ProductEditFieldCallback(field=field, product_id=product_id).pack(),
        )

    builder.button(
        text="🗑 O'chirish",
        callback_data=ProductEditCallback(action="delete", product_id=product_id).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_product_delete_confirmation_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Ha, o'chirish",
        callback_data=ProductEditCallback(action="confirm_delete", product_id=product_id).pack(),
    )
    builder.button(
        text="❌ Yo'q, bekor qilish",
        callback_data=ProductEditCallback(action="cancel_delete", product_id=product_id).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_edit_menu_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Orqaga",
        callback_data=ProductEditCallback(action="select", product_id=product_id).pack(),
    )
    return builder.as_markup()
