from datetime import datetime, timezone
from typing import Optional

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from src.shopim.db.models import Admin
from src.shopim.keyboards.inline.admin.dashboard import (
    DashboardCallback,
    get_dashboard_keyboard,
)
from src.shopim.services.dashboard_service import DashboardService, DashboardStats


from src.shopim.filters import IsAdminFilter


router = Router(name="admin-dashboard-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


def format_dashboard_message(stats: DashboardStats) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        _("<b>📊 Asosiy ko'rsatkichlar</b>\n"
          "_{now} holatiga ko'ra_\n\n"
          "<b>📈 Bugun:</b>\n"
          "  - Buyurtmalar: {orders_today_count} ta\n"
          "  - Tushum: {revenue_today:,.2f} so'm\n"
          "  - Foyda (taxminiy): {profit_today:,.2f} so'm\n\n"
          "<b>⏳ Kutilmoqda:</b>\n"
          "  - Yangi userlar: {pending_registrations_count} ta\n"
          "  - To'lovlar: {pending_topups_count} ta\n"
          "  - Buyurtmalar: {pending_orders_count} ta\n\n"
          "<b>📦 Sklad va Foydalanuvchilar:</b>\n"
          "  - Kam qolgan tovarlar: {low_stock_products_count} ta\n"
          "  - Faol foydalanuvchilar: {active_users_count} ta").format(
            now=now, orders_today_count=stats.orders_today_count, revenue_today=stats.revenue_today,
            profit_today=stats.profit_today, pending_registrations_count=stats.pending_registrations_count,
            pending_topups_count=stats.pending_topups_count, pending_orders_count=stats.pending_orders_count,
            low_stock_products_count=stats.low_stock_products_count, active_users_count=stats.active_users_count
        )
    ).replace(",", " ")


async def show_dashboard(
    target: types.Message | types.CallbackQuery, session: AsyncSession
):
    service = DashboardService(session)
    stats = await service.get_stats()
    text = format_dashboard_message(stats)
    keyboard = get_dashboard_keyboard()

    if isinstance(target, types.CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:  # type: ignore # If message is not modified
            pass
        await target.answer(_("Ma'lumotlar yangilandi"))
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "📊 Dashboard")
async def dashboard_handler(message: types.Message, session: AsyncSession):
    await show_dashboard(message, session)


@router.callback_query(DashboardCallback.filter(F.action == "refresh"))
async def refresh_dashboard_handler(
    callback: types.CallbackQuery, session: AsyncSession
):
    await show_dashboard(callback, session)