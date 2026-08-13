from aiogram import Bot, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.models import User
from src.shopim.db.repositories.admin_repository import AdminRepository

router = Router(name="registration-router")


@router.message(CommandStart(), StateFilter("*"))
async def start_handler(
    message: types.Message, state: FSMContext, bot: Bot, session: AsyncSession, user: User | None
):
    await state.clear()
    settings = get_settings()
    url = settings.get_mini_app_url

    bot_name = "NexШоп"
    full_name = message.from_user.full_name or "Пользователь"

    welcome_text = (
        f"<b>{bot_name}</b> 👥 Добро пожаловать!\n\n"
        f"Здравствуйте, <b>{full_name}</b>!\n"
        f"Используйте наше официальное мини-приложение NexШоп для выбора товаров, совершения покупок, пополнения баланса и управления заказами!"
    )

    if not url:
        await message.answer(
            welcome_text + "\n\n⚠️ <i>Ссылка на Mini App еще не настроена.</i>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        return

    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active) or (message.from_user.id in settings.super_admins_list)

    buttons = [
        [InlineKeyboardButton(text="🍀 Открыть NexШоп Mini App", web_app=WebAppInfo(url=url))]
    ]
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="🛠️ Открыть Панель Админа", web_app=WebAppInfo(url=f"{url}/admin"))
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    
    # Send a separate small empty message to clear any old ReplyKeyboard (reply_markup=ReplyKeyboardRemove())
    # but we can do it directly in message.answer
