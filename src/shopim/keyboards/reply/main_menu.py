from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_user_main_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    if lang == "uz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🛒 Sotib olish"),
                    KeyboardButton(text="📦 Mavjud yuklar"),
                ],
                [
                    KeyboardButton(text="👤 Profil"),
                    KeyboardButton(text="📜 Xaridlar tarixi"),
                ],
                [
                    KeyboardButton(text="💼 Ish! YUQORI MAOSH!"),
                    KeyboardButton(text="🌐 Tilni o'zgartirish"),
                ],
                [
                    KeyboardButton(text="💬 Sharhlar"),
                ],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Купить"),
                    KeyboardButton(text="Наличие"),
                ],
                [
                    KeyboardButton(text="Профиль"),
                    KeyboardButton(text="История покупок"),
                ],
                [
                    KeyboardButton(text="Работа! ПЛАТИМ ДОХУЯ!"),
                    KeyboardButton(text="🌐 Сменить язык"),
                ],
                [
                    KeyboardButton(text="Отзывы"),
                ],
            ],
            resize_keyboard=True,
        )
