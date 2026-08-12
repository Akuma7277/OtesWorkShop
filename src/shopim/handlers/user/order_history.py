from typing import Optional

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from src.shopim.db.models import OrderStatus, User, UserStatus
from src.shopim.keyboards.inline.order_history import (
    OrderHistoryPageCallback,
    ViewOrderCallback,
    get_order_detail_keyboard,
    get_order_history_keyboard,
)
from src.shopim.services.order_history_service import OrderHistoryService


from src.shopim.filters import IsApprovedUserFilter


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

    if result.orders:  # type: ignore
        text = f"<b>Sizning buyurtmalaringiz (Sahifa {result.current_page}/{result.total_pages})</b>"
        keyboard = get_order_history_keyboard(
            orders=result.orders,
            total_pages=result.total_pages,
            current_page=result.current_page,
        )

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore


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
        await callback.answer(_("Buyurtma topilmadi!"), show_alert=True)
        return

    order_status_map = {
        OrderStatus.PENDING_ADMIN: _("⏳ Admin tasdiqlashi kutilmoqda"),
        OrderStatus.APPROVED: _("✅ Tasdiqlangan"),
        OrderStatus.PACKING: _("📦 Qadoqlanmoqda"),
        OrderStatus.OUT_FOR_DELIVERY: _("🚚 Yetkazib berilmoqda"),
        OrderStatus.DELIVERED: _("🏁 Yetkazib berilgan"),
        OrderStatus.REJECTED: _("❌ Rad etilgan"),
        OrderStatus.CANCELLED: _("🚫 Bekor qilingan"),
        OrderStatus.REFUNDED: _("💰 Qaytarilgan"),
        OrderStatus.DRAFT: _("📝 Qoralama"),
    }

    items_text = "\n".join(
        [
            f"  - {item.product_name_snapshot}: {item.grams} gr. = {item.subtotal:.2f} so'm"
            for item in order.items
        ]
    )

    text = (
        _("<b>Buyurtma №{order_number}</b>\n\n"
          "<b>Holati:</b> {status}\n"
          "<b>Sana:</b> {created_at}\n"
          "<b>Jami summa:</b> {total_amount:.2f} so'm\n"
          "<b>Yetkazish manzili:</b> {delivery_address}\n\n"
          "<b>Mahsulotlar:</b>\n{items_text}").format(
            order_number=order.order_number, status=order_status_map.get(order.status, _("Noma'lum")),
            created_at=order.created_at.strftime('%Y-%m-%d %H:%M'), total_amount=order.total_amount,
            delivery_address=order.delivery_address, items_text=items_text
        )
    )

    keyboard = get_order_detail_keyboard(page=callback_data.page)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore
    await callback.answer()