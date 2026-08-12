"""
Mini App handler — /app command opens the Shopim Mini App WebApp.
Also handles fallback to redirect all other text/commands to the Mini App.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, WebAppInfo, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.repositories.admin_repository import AdminRepository

router = Router(name="miniapp-router")


@router.message(Command("app"))
async def open_mini_app(message: Message, session: AsyncSession):
    await send_miniapp_buttons(message, session)


@router.message()
async def fallback_to_miniapp(message: Message, session: AsyncSession):
    # Check if message is a command or text, redirect everything to WebApp
    await send_miniapp_buttons(message, session, is_fallback=True)


async def send_miniapp_buttons(message: Message, session: AsyncSession, is_fallback: bool = False):
    settings = get_settings()
    url = settings.get_mini_app_url

    if not url:
        await message.answer(
            "🛍️ <b>Shopim Mini App</b>\n\n"
            "Mini App hali sozlanmagan. Administrator bilan bog'laning.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        return

    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active) or (message.from_user.id in settings.super_admins_list)

    buttons = [
        [InlineKeyboardButton(text="🛍️ Shopim Mini App'ni ochish", web_app=WebAppInfo(url=url))]
    ]
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="🛠️ Admin Mini App'ni ochish", web_app=WebAppInfo(url=f"{url}/admin"))
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    text = (
        "🛍️ <b>Shopim Mini App</b>\n\n"
        "Premium do'konimizni Telegram ichida to'liq ishlatish uchun quyidagi tugmani bosing!\n\n"
        "✅ Mahsulotlarni ko'ring\n"
        "🛒 Savatga qo'shing\n"
        "📦 Buyurtmalarni kuzating\n"
        "💳 Balans to'ldiring\n"
        "⭐ Sharh qoldiring"
    )

    if is_fallback:
        text = (
            "💬 Barcha bo'limlar <b>Mini App</b>ga o'tkazilgan!\n\n"
            "Botdan foydalanish uchun pastdagi tugmalardan birini bosing:"
        )

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
