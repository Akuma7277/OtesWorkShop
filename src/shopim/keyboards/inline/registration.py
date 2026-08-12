from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

def get_accept_rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("✅ Roziman"), callback_data="register_accept_rules")
            ],
            [
                InlineKeyboardButton(text=_("❌ Bekor qilish"), callback_data="register_cancel")
            ]
        ]
    )
