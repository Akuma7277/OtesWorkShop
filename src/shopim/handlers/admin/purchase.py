from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


class PurchaseConfirmationCallback(CallbackData, prefix="pur_confirm"):
    action: str  # confirm, cancel


def get_purchase_confirmation_keyboard(
    is_balance_sufficient: bool,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_balance_sufficient:
        builder.button(  # type: ignore
            text=_("✅ Tasdiqlash"),
            callback_data=PurchaseConfirmationCallback(action="confirm").pack(),
        )
    builder.button(  # type: ignore
        text=_("❌ Bekor qilish"),
        callback_data=PurchaseConfirmationCallback(action="cancel").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()