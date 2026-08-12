from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("📱 Telefon raqamni yuborish"), request_contact=True)
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
