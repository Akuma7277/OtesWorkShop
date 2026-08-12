from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Dashboard"),
                KeyboardButton(text="🛒 Buyurtmalar"),
            ],
            [
                KeyboardButton(text="👥 Userlar"),
                KeyboardButton(text="➕ Tovar qo'shish"),
            ],
            [
                KeyboardButton(text="✏️ Tovarlarni boshqarish"),
                KeyboardButton(text="💳 Popolneniya"),
            ],
            [KeyboardButton(text="⚙️ Sozlamalar")],
        ],
        resize_keyboard=True,
    )