from typing import Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.types import Message

from src.shopim.db.models import Admin
from src.shopim.keyboards.reply.admin import get_admin_main_keyboard


from src.shopim.filters import IsAdminFilter


router = Router(name="admin-main-menu-router")
router.message.filter(IsAdminFilter())


@router.message(Command("admin"))
async def show_admin_menu(message: Message, admin: Admin):
    await message.answer(
        _("Salom, {full_name}! Admin panelidasiz.").format(full_name=admin.full_name),
        reply_markup=get_admin_main_keyboard(),  # type: ignore
    )