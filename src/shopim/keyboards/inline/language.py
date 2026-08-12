from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class LanguageCallback(CallbackData, prefix="lang"):
    code: str


def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🇺🇿 O'zbekcha", callback_data=LanguageCallback(code="uz").pack()
            ),
            InlineKeyboardButton(
                text="🇷🇺 Русский", callback_data=LanguageCallback(code="ru").pack()
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
