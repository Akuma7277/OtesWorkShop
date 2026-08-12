from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Category


class ProductCreationCallback(CallbackData, prefix="prod_create"):
    action: str  # 'cancel', 'skip_description', 'skip_image'


class ProductCategoryCallback(CallbackData, prefix="prod_cat"):
    action: str  # 'select', 'page'
    category_id: int | None = None
    page: int = 1


def get_cancellation_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("❌ Bekor qilish"),
        callback_data=ProductCreationCallback(action="cancel").pack(),
    )
    return builder.as_markup()


def get_skip_or_cancel_keyboard(skip_action: str, lang: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("⏭ O'tkazib yuborish"),
        callback_data=ProductCreationCallback(action=skip_action).pack(),
    )
    builder.button(
        text=_("❌ Bekor qilish"),
        callback_data=ProductCreationCallback(action="cancel").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_category_selection_keyboard(
    categories: Sequence[Category], total_pages: int, current_page: int, lang: str | None = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat.name,
            callback_data=ProductCategoryCallback(
                action="select", category_id=cat.id, page=current_page
            ).pack(),
        )
    builder.adjust(2)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=ProductCategoryCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=ProductCategoryCallback(action="page", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text=_("❌ Bekor qilish"),
            callback_data=ProductCreationCallback(action="cancel").pack(),
        )
    )
    return builder.as_markup()
