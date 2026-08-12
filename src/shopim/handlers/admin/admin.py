from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("📊 Dashboard")),
                KeyboardButton(text=_("🛒 Buyurtmalar")),
            ],
            [
                KeyboardButton(text=_("👥 Userlar")),
                KeyboardButton(text=_("➕ Tovar qo'shish")),
            ],
            [
                KeyboardButton(text=_("✏️ Tovarlarni boshqarish")),
                KeyboardButton(text=_("💳 Popolneniya")),
            ],
            [KeyboardButton(text=_("⚙️ Sozlamalar"))],
        ],
        resize_keyboard=True,
    )