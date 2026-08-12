"""
Mini App handler — /app command opens the Shopim Mini App WebApp.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.repositories.admin_repository import AdminRepository

router = Router(name="miniapp-router")


@router.message(Command("app"))
async def open_mini_app(message: Message, session: AsyncSession):
    settings = get_settings()
    url = settings.get_mini_app_url  # Auto-detects Railway domain

    if not url:
        await message.answer(
            "🛍️ <b>Shopim Mini App</b>\n\n"
            "Mini App hali sozlanmagan. Administrator bilan bog'laning.",
            parse_mode="HTML",
        )
        return

    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_telegram_id(message.from_user.id)
    is_admin = bool(admin and admin.is_active)

    buttons = [
        [InlineKeyboardButton(text="🛍️ Shopim Mini App'ni ochish", web_app=WebAppInfo(url=url))]
    ]
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="🛠️ Admin Mini App'ni ochish", web_app=WebAppInfo(url=f"{url}/admin"))
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "🛍️ <b>Shopim Mini App</b>\n\n"
        "Premium do'konimizni Telegram ichida to'liq ishlatish uchun quyidagi tugmani bosing!\n\n"
        "✅ Mahsulotlarni ko'ring\n"
        "🛒 Savatga qo'shing\n"
        "📦 Buyurtmalarni kuzating\n"
        "💳 Balans to'ldiring\n"
        "⭐ Sharh qoldiring",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


