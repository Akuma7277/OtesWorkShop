from typing import Sequence

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, User, UserStatus
from src.shopim.filters import IsAdminFilter
from src.shopim.services.user_management_service import UserManagementService

router = Router(name="admin-user-management")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


class UserManageCallback(CallbackData, prefix="user_manage"):
    action: str  # search, page, select
    user_id: int | None = None
    page: int = 1


class UserActionCallback(CallbackData, prefix="user_action"):
    action: str  # toggle_block, adjust_balance, back_to_search
    user_id: int
    page: int


def get_user_search_results_keyboard(
    users: Sequence[User], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in users:
        label = f"{user.full_name} (@{user.username})" if user.username else f"{user.full_name}"
        builder.button(
            text=label,
            callback_data=UserManageCallback(
                action="select", user_id=user.id, page=current_page
            ).pack(),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=UserManageCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=UserManageCallback(action="page", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

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

    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text=_("⬅️ Ro'yxatga qaytish"),
            callback_data=UserManageCallback(action="page", page=page).pack(),
        )
    )
    return builder.as_markup()


@router.message(
    F.text.in_({"👥 Userlar", "👥 Foydalanuvchilar", "👥 Пользователи"}),
    StateFilter("*"),
)
async def user_management_handler(
    message: types.Message, session: AsyncSession, admin: Admin
):
    service = UserManagementService(session)
    result = await service.search_users(query="", page=1)

    text = _("👥 <b>Foydalanuvchilar ro'yxati:</b>\nBoshqarish uchun foydalanuvchini tanlang (bloklash/ko'rish):")

    keyboard = get_user_search_results_keyboard(
        result.users, result.total_pages, result.current_page
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(UserManageCallback.filter(F.action == "page"))
async def paginate_users_handler(
    callback: types.CallbackQuery,
    callback_data: UserManageCallback,
    session: AsyncSession,
    admin: Admin,
):
    service = UserManagementService(session)
    result = await service.search_users(query="", page=callback_data.page)

    text = _("👥 <b>Foydalanuvchilar ro'yxati:</b>\nBoshqarish uchun foydalanuvchini tanlang:")

    keyboard = get_user_search_results_keyboard(
        result.users, result.total_pages, result.current_page
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(UserManageCallback.filter(F.action == "select"))
async def select_user_handler(
    callback: types.CallbackQuery,
    callback_data: UserManageCallback,
    session: AsyncSession,
    admin: Admin,
):
    service = UserManagementService(session)
    user = await service.get_user_by_id(callback_data.user_id)

    if not user:
        await callback.answer(_("Foydalanuvchi topilmadi."), show_alert=True)
        return

    user_label = f"@{user.username}" if user.username else user.full_name
    status_label = "🚫 BLOCKED" if user.status == UserStatus.BLOCKED else "✅ APPROVED"

    text = _(
        "👤 <b>Foydalanuvchi kartochkasi:</b>\n\n"
        "• Ismi: <b>{full_name}</b>\n"
        "• Yuzerneym: <b>{user_label}</b>\n"
        "• Telegram ID: <code>{telegram_id}</code>\n"
        "• Holati: <b>{status_label}</b>\n"
        "• Ro'yxatdan o'tgan sana: {created_at}"
    ).format(
        full_name=user.full_name,
        user_label=user_label,
        telegram_id=user.telegram_id,
        status_label=status_label,
        created_at=user.created_at.strftime('%Y-%m-%d %H:%M'),
    )

    keyboard = get_user_detail_keyboard(user, page=callback_data.page)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(UserActionCallback.filter(F.action == "toggle_block"))
async def toggle_user_block_handler(
    callback: types.CallbackQuery,
    callback_data: UserActionCallback,
    session: AsyncSession,
    admin: Admin,
):
    service = UserManagementService(session)
    user = await service.toggle_user_block(callback_data.user_id, admin)

    if not user:
        await callback.answer(_("Xatolik yuz berdi."), show_alert=True)
        return

    msg = _("Foydalanuvchi holati o'zgartirildi!")
    await callback.answer(msg, show_alert=True)

    keyboard = get_user_detail_keyboard(user, page=callback_data.page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)