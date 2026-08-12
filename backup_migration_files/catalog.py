from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from src.shopim.db.models import Category, Product

# --- CallbackData ---


class CategoryCallback(CallbackData, prefix="cat"):
    action: str  # view
    category_id: int


class ProductCallback(CallbackData, prefix="prod"):
    action: str  # view
    product_id: int
    # For back button
    category_id: int
    page: int


class ProductPageCallback(CallbackData, prefix="prod_page"):
    action: str  # page
    page: int
    category_id: int


class SearchProductCallback(CallbackData, prefix="search_prod"):
    action: str  # view
    product_id: int
    # For back button
    query: str
    page: int


class SearchPageCallback(CallbackData, prefix="search_page"):
    action: str  # page
    page: int
    query: str


class CatalogNavigateCallback(CallbackData, prefix="cat_nav"):
    action: str  # back_to_categories, search


class PurchaseCallback(CallbackData, prefix="buy"):
    action: str  # start
    product_id: int


# --- Keyboards ---


def get_categories_keyboard(categories: Sequence[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=CategoryCallback(action="view", category_id=category.id),
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(  # type: ignore
            text=_("🔍 Mahsulot qidirish"),
            callback_data=CatalogNavigateCallback(action="search").pack(),
        )
    )
    return builder.as_markup()


def get_products_keyboard(
    products: Sequence[Product],
    total_pages: int,
    current_page: int,
    category_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for product in products:
        builder.button(
            text=product.name,
            callback_data=ProductCallback(
                action="view",
                product_id=product.id,
                category_id=category_id,
                page=current_page,
            ),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("⬅️ Orqaga"),
                callback_data=ProductPageCallback(
                    action="page", page=current_page - 1, category_id=category_id
                ).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(  # type: ignore
                text=_("➡️ Oldinga"),
                callback_data=ProductPageCallback(
                    action="page", page=current_page + 1, category_id=category_id
                ).pack(),
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text=_("⤴️ Kategoriyalarga qaytish"),
            callback_data=CatalogNavigateCallback(action="back_to_categories").pack(),
        )
    )

    return builder.as_markup()


def get_product_view_keyboard(
    product_id: int, category_id: int, page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(  # type: ignore
        text=_("🛒 Xarid qilish"),
        callback_data=PurchaseCallback(action="start", product_id=product_id).pack(),
    )
    builder.button(  # type: ignore
        text=_("⬅️ Mahsulotlar ro'yxatiga"),
        callback_data=ProductPageCallback(
            action="page", page=page, category_id=category_id
        ).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_product_view_from_search_keyboard(
    product_id: int, query: str, page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(  # type: ignore
        text=_("🛒 Xarid qilish"),
        callback_data=PurchaseCallback(action="start", product_id=product_id).pack(),
    )
    builder.button(  # type: ignore
        text=_("⬅️ Qidiruv natijalariga"),
        callback_data=SearchPageCallback(action="page", page=page, query=query).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()