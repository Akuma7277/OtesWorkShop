from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


class TopupCallback(CallbackData, prefix="topup"):
    action: str  # 'cancel'


def get_topup_cancellation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("❌ Bekor qilish"),
                    callback_data=TopupCallback(action="cancel").pack(),
                )
            ]
        ]
    )
