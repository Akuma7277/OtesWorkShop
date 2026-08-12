from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

class OrderApprovalCallback(CallbackData, prefix="order_approval"):
    action: str  # 'approve' or 'reject'
    order_id: int

def get_order_approval_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("✅ Tasdiqlash"),
                    callback_data=OrderApprovalCallback(action="approve", order_id=order_id).pack()
                ),
                InlineKeyboardButton(
                    text=_("❌ Rad etish"),
                    callback_data=OrderApprovalCallback(action="reject", order_id=order_id).pack()
                )
            ]
        ]
    )
