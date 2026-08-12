from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.shopim.db.models import Admin
from src.shopim.filters import IsAdminFilter
from src.shopim.keyboards.reply.admin import get_admin_main_keyboard

router = Router(name="admin-main-menu-router")
router.message.filter(IsAdminFilter())


@router.message(Command("admin"))
@router.message(F.text.in_({"⚙️ Sozlamalar", "Admin Panel", "Панель администратора"}))
async def show_admin_menu(message: Message, admin: Admin):
    await message.answer(
        f"Salom, <b>{admin.full_name}</b>! Admin panelidasiz.",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML",
    )