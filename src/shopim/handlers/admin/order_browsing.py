import math
from typing import Sequence

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.shopim.db.models import Admin, Order, OrderItem, OrderStatus
from src.shopim.filters import IsAdminFilter

router = Router(name="admin-order-browsing-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

ITEMS_PER_PAGE = 5


class OrderBrowseCallback(CallbackData, prefix="order_browse"):
    action: str  # page, select
    order_id: int | None = None
    page: int = 1


def get_order_list_keyboard(
    orders: Sequence[Order], total_pages: int, current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for order in orders:
        user_name = order.user.full_name if order.user else "Foydalanuvchi"
        text = f"№{order.order_number} - {user_name} ({order.total_amount:.2f} USD)"
        builder.button(
            text=text,
            callback_data=OrderBrowseCallback(
                action="select", order_id=order.id, page=current_page
            ).pack(),
        )
    builder.adjust(1)

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=OrderBrowseCallback(action="page", page=current_page - 1).pack(),
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=OrderBrowseCallback(action="page", page=current_page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()


@router.message(F.text.in_({"🛒 Buyurtmalar", "🛒 Заказы"}), StateFilter("*"))
async def start_order_browsing_handler(
    message: types.Message, session: AsyncSession, admin: Admin
):
    count_stmt = select(func.count(Order.id))
    total_orders = (await session.execute(count_stmt)).scalar() or 0

    lang = admin.language_code or "uz"
    if total_orders == 0:
        empty_msg = "Hozircha buyurtmalar mavjud emas." if lang == "uz" else "Пока нет заказов."
        await message.answer(empty_msg)
        return

    total_pages = math.ceil(total_orders / ITEMS_PER_PAGE)
    stmt = (
        select(Order)
        .options(joinedload(Order.user))
        .order_by(Order.created_at.desc())
        .limit(ITEMS_PER_PAGE)
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()

    text = (
        f"🛒 <b>Barcha buyurtmalar ro'yxati (Jami: {total_orders} ta):</b>\nBatafsil ko'rish uchun buyurtmani tanlang:"
        if lang == "uz"
        else f"🛒 <b>Список всех заказов (Всего: {total_orders}):</b>\nВыберите заказ для просмотра:"
    )

    keyboard = get_order_list_keyboard(orders, total_pages, 1)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(OrderBrowseCallback.filter(F.action == "page"))
async def paginate_orders_handler(
    callback: types.CallbackQuery,
    callback_data: OrderBrowseCallback,
    session: AsyncSession,
    admin: Admin,
):
    count_stmt = select(func.count(Order.id))
    total_orders = (await session.execute(count_stmt)).scalar() or 0
    total_pages = math.ceil(total_orders / ITEMS_PER_PAGE)

    offset = (callback_data.page - 1) * ITEMS_PER_PAGE
    stmt = (
        select(Order)
        .options(joinedload(Order.user))
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(ITEMS_PER_PAGE)
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()

    lang = admin.language_code or "uz"
    text = (
        f"🛒 <b>Barcha buyurtmalar ro'yxati (Sahifa {callback_data.page}/{total_pages}):</b>"
        if lang == "uz"
        else f"🛒 <b>Список заказов (Страница {callback_data.page}/{total_pages}):</b>"
    )

    keyboard = get_order_list_keyboard(orders, total_pages, callback_data.page)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(OrderBrowseCallback.filter(F.action == "select"))
async def select_order_handler(
    callback: types.CallbackQuery,
    callback_data: OrderBrowseCallback,
    session: AsyncSession,
    admin: Admin,
):
    stmt = (
        select(Order)
        .options(joinedload(Order.user), joinedload(Order.items).joinedload(OrderItem.product))
        .where(Order.id == callback_data.order_id)
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return

    lang = admin.language_code or "uz"
    user_label = f"@{order.user.username}" if (order.user and order.user.username) else (order.user.full_name if order.user else "Klient")

    items_summary = "\n".join(
        [f"  • {item.product.name if item.product else 'Tovar'}: <b>{item.grams} gr</b> x <b>{item.unit_price_per_gram:.2f} USD</b>" for item in order.items]
    )

    if lang == "ru":
        text = (
            f"📦 <b>Заказ №{order.order_number}</b>\n\n"
            f"• Клиент: <b>{user_label}</b> (ID: <code>{order.user.telegram_id if order.user else 0}</code>)\n"
            f"• Статус: <b>{order.status.value}</b>\n"
            f"• Сумма: <b>{order.total_amount:.2f} USD</b>\n"
            f"• Дата: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"<b>Товары:</b>\n{items_summary}"
        )
    else:
        text = (
            f"📦 <b>Buyurtma №{order.order_number}</b>\n\n"
            f"• Mijoz: <b>{user_label}</b> (ID: <code>{order.user.telegram_id if order.user else 0}</code>)\n"
            f"• Holati: <b>{order.status.value}</b>\n"
            f"• Summasi: <b>{order.total_amount:.2f} USD</b>\n"
            f"• Sana: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"<b>Tovarlar:</b>\n{items_summary}"
        )

    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Ro'yxatga qaytish / К списку",
        callback_data=OrderBrowseCallback(action="page", page=callback_data.page).pack(),
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()