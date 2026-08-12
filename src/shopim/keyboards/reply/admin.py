from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def get_admin_main_keyboard(lang: str | None = None) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("📊 Dashboard")),
                KeyboardButton(text=_("🛒 Buyurtmalar")),
            ],
            [
                KeyboardButton(text=_("👥 Foydalanuvchilar")),
                KeyboardButton(text=_("➕ Tovar qo'shish")),
            ],
            [
                KeyboardButton(text=_("✏️ Tovarlarni boshqarish")),
                KeyboardButton(text=_("💳 To'lovlar")),
            ],
            [
                KeyboardButton(text=_("⚙️ Sozlamalar")),
            ],
        ],
        resize_keyboard=True,
    )