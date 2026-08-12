from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class TopupCallback(CallbackData, prefix="topup"):
    action: str  # 'cancel'


def get_topup_cancellation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=TopupCallback(action="cancel").pack(),
                )
            ]
        ]
    )
