from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_admin_main_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    if lang == "ru":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="📊 Dashboard"),
                    KeyboardButton(text="🛒 Заказы"),
                ],
                [
                    KeyboardButton(text="👥 Пользователи"),
                    KeyboardButton(text="➕ Добавить товар"),
                ],
                [
                    KeyboardButton(text="✏️ Управление товарами"),
                    KeyboardButton(text="💳 Пополнения"),
                ],
                [
                    KeyboardButton(text="⚙️ Настройки"),
                ],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="📊 Dashboard"),
                    KeyboardButton(text="🛒 Buyurtmalar"),
                ],
                [
                    KeyboardButton(text="👥 Foydalanuvchilar"),
                    KeyboardButton(text="➕ Tovar qo'shish"),
                ],
                [
                    KeyboardButton(text="✏️ Tovarlarni boshqarish"),
                    KeyboardButton(text="💳 To'lovlar"),
                ],
                [
                    KeyboardButton(text="⚙️ Sozlamalar"),
                ],
            ],
            resize_keyboard=True,
        )