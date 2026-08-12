from typing import Sequence

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from src.shopim.db.models import User, UserStatus

router = Router(name="admin-user-management")
class UserManageCallback(CallbackData, prefix="user_manage"):
    action: str  # search, page, select
    user_id: int | None = None
    page: int = 1


class UserActionCallback(CallbackData, prefix="user_action"):
    action: str  # toggle_block, adjust_balance, back_to_search
    user_id: int
    page: int  # To return to the correct page of search results


def get_user_management_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("🔍 Foydalanuvchini qidirish"),
        callback_data=UserManageCallback(action="search").pack(),
    )
    return builder.as_markup()


def get_user_search_results_keyboard(
    users: Sequence[User], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(  # type: ignore
            text=_("{full_name} (ID: {user_id})").format(full_name=user.full_name, user_id=user.id),
            callback_data=UserManageCallback(
                action="select", user_id=user.id, page=current_page
            ).pack(),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("⬅️"),
                callback_data=UserManageCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("➡️"),
                callback_data=UserManageCallback(action="page", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text=_("⤴️ Yangi qidiruv"),
            callback_data=UserManageCallback(action="search").pack(),
        )
    )
    return builder.as_markup()


def get_user_detail_keyboard(user: User, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if user.status == UserStatus.BLOCKED:
        builder.button(
            text=_("🔓 Blokdan chiqarish"),
            callback_data=UserActionCallback(
                action="toggle_block", user_id=user.id, page=page
            ).pack(),
        )
    else:
        builder.button(
            text=_("🚫 Bloklash"),
            callback_data=UserActionCallback(
                action="toggle_block", user_id=user.id, page=page
            ).pack(),
        )

    builder.button(
        text=_("💰 Balansni o'zgartirish"),
        callback_data=UserActionCallback(
            action="adjust_balance", user_id=user.id, page=page
        ).pack(),
    )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text=_("⬅️ Qidiruv natijalariga"),
            callback_data=UserManageCallback(action="page", page=page).pack(),
        )
    )
    return builder.as_markup()


def get_back_to_user_detail_keyboard(user_id: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("⬅️ Orqaga"),
        callback_data=UserManageCallback(
            action="select", user_id=user_id, page=page
        ).pack(),
    )
    return builder.as_markup()