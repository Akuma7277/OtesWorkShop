from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.shopim.utils.i18n_messages import t


def get_admin_main_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("admin_keyboard_dashboard", lang)),
                KeyboardButton(text=t("admin_keyboard_orders", lang)),
            ],
            [
                KeyboardButton(text=t("admin_keyboard_users", lang)),
                KeyboardButton(text=t("admin_keyboard_add_product", lang)),
            ],
            [
                KeyboardButton(text=t("admin_keyboard_edit_products", lang)),
                KeyboardButton(text=t("admin_keyboard_topups", lang)),
            ],
            [
                KeyboardButton(text=t("admin_keyboard_settings", lang)),
            ],
        ],
        resize_keyboard=True,
    )