from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.core.settings_models import BotSettings


class SettingsCallback(CallbackData, prefix="settings"):
    action: str  # 'choose_field', 'back_to_menu', 'toggle_admin_lang'
    field: str | None = None


def get_settings_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=_("🌐 Admin tilini o'zgartirish"),
        callback_data=SettingsCallback(action="toggle_admin_lang").pack(),
    )

    for name, field in BotSettings.model_fields.items():
        label = field.description or name
        builder.button(
            text=f"✏️ {label}",
            callback_data=SettingsCallback(action="choose_field", field=name).pack(),
        )

    builder.adjust(1)
    return builder.as_markup()


def get_back_to_settings_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("⬅️ Orqaga"),
        callback_data=SettingsCallback(action="back_to_menu").pack(),
    )
    return builder.as_markup()
