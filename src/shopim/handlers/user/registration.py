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
    full_name = message.from_user.full_name or "Foydalanuvchi"

    # Detect language
    lang = "uz"
    if user and user.language_code:
        lang = user.language_code
    elif message.from_user.language_code:
        tg_lang = message.from_user.language_code.lower()
        if tg_lang.startswith("ru"):
            lang = "ru"

    if lang == "ru":
        welcome_text = (
            f"<b>{bot_name}</b> 👥 Добро пожаловать!\n\n"
            f"Здравствуйте, <b>{full_name}</b>!\n"
            f"Используйте наше официальное мини-приложение NexШоп для выбора товаров, совершения покупок, пополнения баланса и управления заказами!"
        )
        warning_text = "\n\n⚠️ <i>Ссылка на Mini App еще не настроена.</i>"
        btn_app_text = "🍀 Открыть NexШоп Mini App"
        btn_admin_text = "🛠️ Открыть Панель Админа"
    else:
        welcome_text = (
            f"<b>{bot_name}</b> 👥 Xush kelibsiz!\n\n"
            f"Assalomu alaykum, <b>{full_name}</b>!\n"
            f"Mahsulotlarni tanlash, xarid qilish, balansni to'ldirish va buyurtmalarni boshqarish uchun bizning rasmiy NexШоп mini-ilovamizdan foydalaning!"
        )
        warning_text = "\n\n⚠️ <i>Mini App havolasi hali sozlanmagan.</i>"
        btn_app_text = "🍀 NexШоп Mini Appni ochish"
        btn_admin_text = "🛠️ Admin panelni ochish"

    if not url:
        await message.answer(
            welcome_text + warning_text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        return

    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active) or (message.from_user.id in settings.super_admins_list)

    buttons = [
        [InlineKeyboardButton(text=btn_app_text, web_app=WebAppInfo(url=url))]
    ]
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text=btn_admin_text, web_app=WebAppInfo(url=f"{url}/admin"))
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    
    # Send a separate small empty message to clear any old ReplyKeyboard (reply_markup=ReplyKeyboardRemove())
    # but we can do it directly in message.answer
