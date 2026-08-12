from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_user_main_keyboard() -> ReplyKeyboardMarkup:
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
            ],
            [
                KeyboardButton(text="Отзывы"),
            ],
        ],
        resize_keyboard=True,
    )
