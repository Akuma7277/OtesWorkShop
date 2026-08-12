from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TopupActionCallback(CallbackData, prefix="topup_action"):
    action: str  # 'approve' or 'reject'
    topup_id: int


TopupReviewCallback = TopupActionCallback


class TopupManageCallback(CallbackData, prefix="topup_manage"):
    action: str  # 'page'
    page: int = 1


def get_topup_review_keyboard(topup_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=TopupActionCallback(action="approve", topup_id=topup_id).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=TopupActionCallback(action="reject", topup_id=topup_id).pack(),
                ),
            ]
        ]
    )


def get_pending_topups_keyboard(
    total_pages: int, current_page: int
) -> InlineKeyboardMarkup | None:
    if total_pages <= 1:
        return None

    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=TopupManageCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=TopupManageCallback(action="page", page=current_page + 1).pack(),
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()
