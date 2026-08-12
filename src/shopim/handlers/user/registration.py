from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard

router = Router(name="registration-router")


@router.message(CommandStart())
async def start_handler(
    message: types.Message, state: FSMContext, user: User | None
):
    await state.clear()
    full_name = message.from_user.full_name or "клиент"
    welcome_text = (
        f"<b>Don Huan Syndicate</b> Hola amigos 👥, Добро пожаловать!\n\n"
        f"Здравствуйте, <b>{full_name}</b>!\n"
        f"Воспользуйтесь меню ниже для выбора товаров и совершения покупок."
    )
    await message.answer(
        welcome_text,
        reply_markup=get_user_main_keyboard(),
        parse_mode="HTML",
    )
