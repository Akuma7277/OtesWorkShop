from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_accept_rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Roziman", callback_data="register_accept_rules")
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="register_cancel")
            ]
        ]
    )
