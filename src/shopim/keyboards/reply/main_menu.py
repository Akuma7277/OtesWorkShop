from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def get_user_main_keyboard(is_admin: bool = False, lang: str | None = None) -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(text=_("🛒 Sotib olish", locale=lang)),
            KeyboardButton(text=_("📦 Mavjud yuklar", locale=lang)),
        ],
        [
            KeyboardButton(text=_("👤 Profil", locale=lang)),
            KeyboardButton(text=_("📜 Xaridlar tarixi", locale=lang)),
        ],
        [
            KeyboardButton(text=_("💼 Ish! YUQORI MAOSH!", locale=lang)),
            KeyboardButton(text=_("🌐 Tilni o'zgartirish", locale=lang)),
        ],
        [
            KeyboardButton(text=_("💬 Sharhlar", locale=lang)),
        ],
    ]
    if is_admin:
        rows.append([KeyboardButton(text=_("🛠 Admin Paneli", locale=lang))])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
    )

