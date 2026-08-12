from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.shopim.utils.i18n_messages import t


def get_user_main_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("user_keyboard_buy", lang)),
                KeyboardButton(text=t("user_keyboard_stock", lang)),
            ],
            [
                KeyboardButton(text=t("user_keyboard_profile", lang)),
                KeyboardButton(text=t("user_keyboard_history", lang)),
            ],
            [
                KeyboardButton(text=t("user_keyboard_jobs", lang)),
                KeyboardButton(text=t("user_keyboard_lang", lang)),
            ],
            [
                KeyboardButton(text=t("user_keyboard_reviews", lang)),
            ],
        ],
        resize_keyboard=True,
    )
