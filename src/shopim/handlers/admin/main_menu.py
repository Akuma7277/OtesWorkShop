from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, AdminRole
from src.shopim.db.repositories.admin_repository import AdminRepository
from src.shopim.keyboards.reply.admin import get_admin_main_keyboard
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard
from src.shopim.core.config import get_settings


router = Router(name="admin-main-menu-router")


@router.message(Command("admin"), StateFilter("*"))
@router.message(
    F.text.in_({
        "Admin Panel", "Панель администратора", "⚙️ Admin Panel", "🛠 Admin Paneli", "Admin paneli"
    }),
    StateFilter("*"),
)
async def show_admin_menu(
    message: Message, session: AsyncSession, state: FSMContext, admin: Optional[Admin] = None
):
    await state.clear()
    if not admin:
        admin_repo = AdminRepository(session)
        admin = await admin_repo.get_by_telegram_id(message.from_user.id)
        if not admin:
            admin = Admin(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name or "Super Admin",
                role=AdminRole.SUPER_ADMIN,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

    welcome_text = _(
        "Salom, <b>{full_name}</b>! Admin panelidasiz.\n"
        "Roli: <b>{role}</b>\n\n"
        "🛠️ Admin panelni to'liq premium Mini App'da boshqarish uchun pastdagi tugmani bosing!"
    ).format(full_name=admin.full_name, role=admin.role.value)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    settings = get_settings()
    url = settings.get_mini_app_url
    
    keyboard = get_admin_main_keyboard()
    if url:
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🛠️ Admin Mini App'ni ochish", web_app=WebAppInfo(url=f"{url}/admin"))
        ]])
        await message.answer(welcome_text, reply_markup=inline_kb, parse_mode="HTML")
    else:
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")



@router.message(Command("user"), StateFilter("*"))
@router.message(
    F.text.in_({
        "🏠 Foydalanuvchi bo'limi", "🏠 Foydalanuvchi rejimi", "🏠 User bo'limi",
        "🏠 Режим пользователя", "Foydalanuvchi bo'limi", "User bo'limi"
    }),
    StateFilter("*"),
)
async def switch_to_user_mode(
    message: Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active)

    welcome_text = _(
        "🏠 <b>Foydalanuvchi bo'limiga o'tildi.</b>\n\n"
        "Mahsulotlar va xizmatlardan foydalanish uchun pastdagi menyuni tanlang:"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_user_main_keyboard(is_admin=is_admin),
        parse_mode="HTML",
    )


@router.message(Command("menu"), StateFilter("*"))
async def menu_command_handler(
    message: Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active)

    if is_admin:
        await show_admin_menu(message, session, state, admin)
    else:
        await message.answer(
            _("📋 <b>Asosiy menyu:</b>"),
            reply_markup=get_user_main_keyboard(is_admin=False),
            parse_mode="HTML",
        )


@router.message(Command("cancel"), StateFilter("*"))
@router.message(
    F.text.in_({"🚫 Bekor qilish", "🚫 Отмена", "Bekor qilish", "Отмена"}),
    StateFilter("*"),
)
async def cancel_command_handler(
    message: Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active)

    await message.answer(
        _("🚫 Barcha amallar bekor qilindi."),
        reply_markup=get_admin_main_keyboard() if is_admin else get_user_main_keyboard(is_admin=False),
    )