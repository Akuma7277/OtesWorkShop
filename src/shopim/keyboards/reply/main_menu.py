from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def get_user_main_keyboard(lang: str | None = None) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("🛒 Sotib olish")),
                KeyboardButton(text=_("📦 Mavjud yuklar")),
            ],
            [
                KeyboardButton(text=_("👤 Profil")),
                KeyboardButton(text=_("📜 Xaridlar tarixi")),
            ],
            [
                KeyboardButton(text=_("💼 Ish! YUQORI MAOSH!")),
                KeyboardButton(text=_("🌐 Tilni o'zgartirish")),
            ],
            [
                KeyboardButton(text=_("💬 Sharhlar")),
            ],
        ],
        resize_keyboard=True,
    )
