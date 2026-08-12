from aiogram import Bot, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

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
    full_name = message.from_user.full_name or "клиент"
    lang = user.language_code if user else "ru"

    if lang == "uz":
        welcome_text = (
            f"<b>{bot_name}</b> 👥 Xush kelibsiz!\n\n"
            f"Assalomu alaykum, <b>{full_name}</b>!\n"
            f"Mahsulotlarni tanlash va xarid qilish uchun pastdagi menyudan foydalaning."
        )
    else:
        welcome_text = (
            f"<b>{bot_name}</b> 👥 Добро пожаловать!\n\n"
            f"Здравствуйте, <b>{full_name}</b>!\n"
            f"Воспользуйтесь меню ниже для выбора товаров и совершения покупок."
        )

    await message.answer(
        welcome_text,
        reply_markup=get_user_main_keyboard(lang),
        parse_mode="HTML",
    )
