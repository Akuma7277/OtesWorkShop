from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, AdminRole
from src.shopim.db.repositories.admin_repository import AdminRepository
from src.shopim.keyboards.reply.admin import get_admin_main_keyboard

router = Router(name="admin-main-menu-router")


@router.message(Command("admin"), StateFilter("*"))
@router.message(
    F.text.in_({"⚙️ Sozlamalar", "⚙️ Настройки", "Admin Panel", "Панель администратора"}),
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

    lang = admin.language_code or "uz"
    if lang == "ru":
        welcome_text = (
            f"Здравствуйте, <b>{admin.full_name}</b>! Вы в панели администратора.\n"
            f"Роль: <b>{admin.role.value}</b>"
        )
    else:
        welcome_text = (
            f"Salom, <b>{admin.full_name}</b>! Admin panelidasiz.\n"
            f"Roli: <b>{admin.role.value}</b>"
        )

    await message.answer(
        welcome_text,
        reply_markup=get_admin_main_keyboard(lang),
        parse_mode="HTML",
    )