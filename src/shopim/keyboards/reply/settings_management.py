from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.core.settings_models import BotSettings


class SettingsCallback(CallbackData, prefix="settings"):
    action: str  # choose_field, back_to_menu
    field: str | None = None


def get_settings_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Get fields and their descriptions from the Pydantic model
    fields = BotSettings.model_fields

    for field_name, field_info in fields.items():
        builder.button(
            text=f"✏️ {field_info.description or field_name}",
            callback_data=SettingsCallback(action="choose_field", field=field_name),
        )

    builder.adjust(1)
    return builder.as_markup()


def get_back_to_settings_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Sozlamalar menyusiga",
        callback_data=SettingsCallback(action="back_to_menu").pack(),
    )
    return builder.as_markup()