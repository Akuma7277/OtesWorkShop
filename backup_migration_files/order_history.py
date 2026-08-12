from typing import Optional

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import OrderStatus, User, UserStatus
from src.shopim.keyboards.inline.order_history import (
    OrderHistoryPageCallback,
    ViewOrderCallback,
    get_order_detail_keyboard,
    get_order_history_keyboard,
)
from src.shopim.services.order_history_service import OrderHistoryService

ORDER_STATUS_MAP = {
    OrderStatus.PENDING_ADMIN: "⏳ Admin tasdiqlashi kutilmoqda",
    OrderStatus.APPROVED: "✅ Tasdiqlangan",
    OrderStatus.PACKING: "📦 Qadoqlanmoqda",
    OrderStatus.OUT_FOR_DELIVERY: "🚚 Yetkazib berilmoqda",
    OrderStatus.DELIVERED: "🏁 Yetkazib berilgan",
    OrderStatus.REJECTED: "❌ Rad etilgan",
    OrderStatus.CANCELLED: "🚫 Bekor qilingan",
    OrderStatus.REFUNDED: "💰 Qaytarilgan",
    OrderStatus.DRAFT: "📝 Qoralama",
}


class IsApprovedUserFilter:
    def __call__(self, user: Optional[User]) -> bool:
        return user is not None and user.status == UserStatus.APPROVED


router = Router(name="order-history-router")
router.message.filter(IsApprovedUserFilter())
router.callback_query.filter(IsApprovedUserFilter())

ORDERS_PER_PAGE = 5


async def show_paginated_orders(
    target: types.Message | types.CallbackQuery, user: User, page: int, session: AsyncSession
):
    service = OrderHistoryService(session, orders_per_page=ORDERS_PER_PAGE)
    result = await service.get_user_orders(user.id, page)

    text = "Sizda hali buyurtmalar mavjud emas."
    keyboard = None

    if result.orders:
        text = f"<b>Sizning buyurtmalaringiz (Sahifa {result.current_page}/{result.total_pages})</b>"
        keyboard = get_order_history_keyboard(
            orders=result.orders,
            total_pages=result.total_pages,
            current_page=result.current_page,
        )

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "📦 Buyurtmalarim")
async def show_order_history_handler(
    message: types.Message, user: User, session: AsyncSession
):
    await show_paginated_orders(message, user, 1, session)


@router.callback_query(OrderHistoryPageCallback.filter())
async def paginate_order_history_handler(
    callback: types.CallbackQuery,
    callback_data: OrderHistoryPageCallback,
    user: User,
    session: AsyncSession,
):
    await show_paginated_orders(callback, user, callback_data.page, session)
    await callback.answer()


@router.callback_query(ViewOrderCallback.filter())
async def view_order_detail_handler(
    callback: types.CallbackQuery,
    callback_data: ViewOrderCallback,
    user: User,
    session: AsyncSession,
):
    service = OrderHistoryService(session)
    order = await service.get_order_details(callback_data.order_id, user.id)

    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    items_text = "\n".join(
        [
            f"  - {item.product_name_snapshot}: {item.grams} gr. = {item.subtotal:.2f} so'm"
            for item in order.items
        ]
    )

    text = (
        f"<b>Buyurtma №{order.order_number}</b>\n\n"
        f"<b>Holati:</b> {ORDER_STATUS_MAP.get(order.status, 'Noma\'lum')}\n"
        f"<b>Sana:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>Jami summa:</b> {order.total_amount:.2f} so'm\n"
        f"<b>Yetkazish manzili:</b> {order.delivery_address}\n\n"
        f"<b>Mahsulotlar:</b>\n{items_text}"
    )

    keyboard = get_order_detail_keyboard(page=callback_data.page)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()