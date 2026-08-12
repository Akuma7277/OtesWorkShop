from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛍 Katalog"),
                KeyboardButton(text="💰 Balansim")
            ],
            [
                KeyboardButton(text="➕ Balans to'ldirish"),
                KeyboardButton(text="📦 Buyurtmalarim"),
            ],
            [
                KeyboardButton(text="👤 Profilim"),
                KeyboardButton(text="📞 Operator bilan aloqa"),
            ],
            [KeyboardButton(text="ℹ️ Qoidalar")],
        ],
        resize_keyboard=True,
    )