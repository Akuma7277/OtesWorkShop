from aiogram import Bot, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.shopim.db.models import User
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard

router = Router(name="registration-router")


@router.message(CommandStart(), StateFilter("*"))
async def start_handler(
    message: types.Message, state: FSMContext, bot: Bot, user: User | None
):
    await state.clear()
    bot_info = await bot.get_me()
    bot_name = bot_info.first_name or "Shopim"
    full_name = message.from_user.full_name or _("mijoz")

    welcome_text = _(
        "<b>{bot_name}</b> 👥 Xush kelibsiz!\n\n"
        "Assalomu alaykum, <b>{full_name}</b>!\n"
        "Mahsulotlarni tanlash va xarid qilish uchun pastdagi menyudan foydalaning."
    ).format(bot_name=bot_name, full_name=full_name)

    await message.answer(
        welcome_text,
        reply_markup=get_user_main_keyboard(),
        parse_mode="HTML",
    )
