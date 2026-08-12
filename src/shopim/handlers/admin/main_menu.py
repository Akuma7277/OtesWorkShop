from typing import Optional
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, AdminRole
from src.shopim.db.repositories.admin_repository import AdminRepository
from src.shopim.keyboards.reply.admin import get_admin_main_keyboard

router = Router(name="admin-main-menu-router")


@router.message(Command("admin"))
@router.message(F.text.in_({"⚙️ Sozlamalar", "Admin Panel", "Панель администратора"}))
async def show_admin_menu(
    message: Message, session: AsyncSession, admin: Optional[Admin] = None
):
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

    await message.answer(
        f"Salom, <b>{admin.full_name}</b>! Admin panelidasiz.\n"
        f"Роль: <b>{admin.role.value}</b>",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML",
    )