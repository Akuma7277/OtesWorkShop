from datetime import datetime, timezone
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin
from src.shopim.filters import IsAdminFilter
from src.shopim.keyboards.inline.admin.dashboard import (
    DashboardCallback,
    get_buyers_keyboard,
    get_dashboard_keyboard,
)
from src.shopim.services.dashboard_service import DashboardService, DashboardStats

router = Router(name="admin-dashboard-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


def format_dashboard_message(stats: DashboardStats, lang: str | None = None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = _(
        "<b>📊 Tizim Analitikasi va Moliyaviy Grafik</b>\n"
        "<i>{now} holatiga ko'ra avto-yangilandi</i>\n\n"
        "<b>📈 Bugungi Ko'rsatkichlar:</b>\n"
        "  • Tushgan buyurtmalar: <b>{orders_today_count} ta</b>\n"
        "  • Tushgan tushum: <b>{revenue_today:,.2f} USD</b>\n"
        "  • Taxminiy sof foyda: <b>{profit_today:,.2f} USD</b>\n\n"
        "<b>💎 Barcha Vaqtlardagi Statistika:</b>\n"
        "  • Jami tushgan pullar: <b>{total_revenue:,.2f} USD</b>\n"
        "  • Ketgan (sotilgan) tovarlar: <b>{total_grams_sold:,.2f} gramm</b>\n"
        "  • Jami buyurtmalar soni: <b>{total_orders_count} ta</b>\n\n"
        "<b>⏳ Kutilayotgan harakatlar:</b>\n"
        "  • Kutilayotgan to'lovlar: <b>{pending_topups_count} ta</b>\n"
        "  • Tasdiqlanmagan buyurtmalar: <b>{pending_orders_count} ta</b>\n\n"
        "<b>📦 Ombordagi holat va Foydalanuvchilar:</b>\n"
        "  • Ogohlantirish (oz qolgan): <b>{low_stock_products_count} ta tovar</b>\n"
        "  • Faol xaridorlar (botda): <b>{active_users_count} ta</b>"
    ).format(
        now=now,
        orders_today_count=stats.orders_today_count,
        revenue_today=stats.revenue_today,
        profit_today=stats.profit_today,
        total_revenue=stats.total_revenue,
        total_grams_sold=stats.total_grams_sold,
        total_orders_count=stats.total_orders_count,
        pending_topups_count=stats.pending_topups_count,
        pending_orders_count=stats.pending_orders_count,
        low_stock_products_count=stats.low_stock_products_count,
        active_users_count=stats.active_users_count,
    )
    return text.replace(",", " ")


def format_buyers_message(stats: DashboardStats, lang: str | None = None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        _("<b>👥 Top Xaridorlar Ro'yxati (Kimlar tovar olgan):</b>"),
        f"<i>{now} holatiga ko'ra</i>\n",
    ]
    if not stats.top_buyers:
        lines.append(_("<i>Hozircha xaridlar mavjud emas.</i>"))
    else:
        for idx, (u, count, spent, grams) in enumerate(stats.top_buyers, 1):
            user_label = f"@{u.username}" if u.username else u.full_name
            entry = _(
                "<b>{idx}. {user_label}</b> (ID: <code>{telegram_id}</code>)\n"
                "   • Buyurtmalar: <b>{count} ta</b> | Soni/Og'irligi: <b>{grams:,.2f} gr</b>\n"
                "   • Sarflagan summasi: <b>{spent:,.2f} USD</b>\n"
            ).format(
                idx=idx,
                user_label=user_label,
                telegram_id=u.telegram_id,
                count=count,
                grams=grams,
                spent=spent,
            )
            lines.append(entry)

    return "\n".join(lines).replace(",", " ")


async def show_dashboard(
    target: types.Message | types.CallbackQuery, session: AsyncSession, admin: Admin
):
    service = DashboardService(session)
    stats = await service.get_stats()
    text = format_dashboard_message(stats)
    keyboard = get_dashboard_keyboard()

    if isinstance(target, types.CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            pass
        await target.answer(_("Analitika yangilandi!"))
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text.in_({"📊 Dashboard", "📊 Analitika", "Analitika", "Dashboard"}), StateFilter("*"))
async def dashboard_handler(message: types.Message, session: AsyncSession, admin: Admin):
    await show_dashboard(message, session, admin)


@router.callback_query(DashboardCallback.filter(F.action == "refresh"))
async def refresh_dashboard_handler(
    callback: types.CallbackQuery, session: AsyncSession, admin: Admin
):
    await show_dashboard(callback, session, admin)


@router.callback_query(DashboardCallback.filter(F.action == "buyers"))
async def buyers_dashboard_handler(
    callback: types.CallbackQuery, session: AsyncSession, admin: Admin
):
    service = DashboardService(session)
    stats = await service.get_stats()
    text = format_buyers_message(stats)
    keyboard = get_buyers_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer(_("Xaridorlar ro'yxati yangilandi!"))


@router.callback_query(DashboardCallback.filter(F.action == "main_stats"))
async def main_stats_dashboard_handler(
    callback: types.CallbackQuery, session: AsyncSession, admin: Admin
):
    await show_dashboard(callback, session, admin)