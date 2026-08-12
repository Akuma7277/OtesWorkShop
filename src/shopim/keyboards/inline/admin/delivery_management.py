from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.shopim.db.models import Order, OrderStatus


class DeliveryActionCallback(CallbackData, prefix="delivery"):
    action: str  # set_status
    order_id: int
    status: str
    page: int


def get_delivery_action_keyboard(order: Order, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if order.status == OrderStatus.APPROVED:
        builder.button(
            text="📦 Qadoqlashni boshlash",
            callback_data=DeliveryActionCallback(
                action="set_status",
                order_id=order.id,
                status=OrderStatus.PACKING.name,
                page=page,
            ),
        )
    elif order.status == OrderStatus.PACKING:
        builder.button(
            text="🚚 Yo'lga chiqdi",
            callback_data=DeliveryActionCallback(
                action="set_status",
                order_id=order.id,
                status=OrderStatus.OUT_FOR_DELIVERY.name,
                page=page,
            ),
        )
    elif order.status == OrderStatus.OUT_FOR_DELIVERY:
        builder.button(
            text="🏁 Yetkazib berildi",
            callback_data=DeliveryActionCallback(
                action="set_status",
                order_id=order.id,
                status=OrderStatus.DELIVERED.name,
                page=page,
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Qidiruv natijalariga",
            callback_data=f"order_browse:page::{page}",
        )
    )
    builder.adjust(1)
    return builder.as_markup()
