from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def get_admin_main_keyboard(lang: str | None = None) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("📊 Dashboard", locale=lang)),
                KeyboardButton(text=_("🛒 Buyurtmalar", locale=lang)),
            ],
            [
                KeyboardButton(text=_("👥 Foydalanuvchilar", locale=lang)),
                KeyboardButton(text=_("➕ Tovar qo'shish", locale=lang)),
            ],
            [
                KeyboardButton(text=_("✏️ Tovarlarni boshqarish", locale=lang)),
                KeyboardButton(text=_("💳 To'lovlar", locale=lang)),
            ],
            [
                KeyboardButton(text=_("⚙️ Sozlamalar", locale=lang)),
                KeyboardButton(text=_("🏠 Foydalanuvchi bo'limi", locale=lang)),
            ],
        ],
        resize_keyboard=True,
    )