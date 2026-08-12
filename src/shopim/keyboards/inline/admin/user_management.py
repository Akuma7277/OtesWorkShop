from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class UserApprovalCallback(CallbackData, prefix="user_approval"):
    action: str  # 'approve' or 'reject'
    user_id: int

def get_user_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=UserApprovalCallback(action="approve", user_id=user_id).pack()
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=UserApprovalCallback(action="reject", user_id=user_id).pack()
                )
            ]
        ]
    )
