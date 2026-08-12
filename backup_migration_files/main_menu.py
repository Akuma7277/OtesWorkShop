from typing import Optional

from aiogram import F, Router, types

from src.shopim.db.models import User, UserStatus
from src.shopim.keyboards.reply.user import get_main_keyboard


class IsApprovedUserFilter:
    def __call__(self, user: Optional[User]) -> bool:
        return user is not None and user.status == UserStatus.APPROVED


router = Router(name="main-menu-router")
router.message.filter(IsApprovedUserFilter())

@router.message(F.text == "/start")
async def show_main_menu(message: types.Message, user: User):
    await message.answer(
        f"Assalomu alaykum, {user.full_name}! Asosiy menyudasiz.",
        reply_markup=get_main_keyboard(),
    )