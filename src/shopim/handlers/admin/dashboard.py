from datetime import datetime, timezone
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import StateFilter
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


def format_dashboard_message(stats: DashboardStats, lang: str = "uz") -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if lang == "ru":
        return (
            f"<b>📊 Аналитика системы и Финансовый График</b>\n"
            f"<i>Авто-обновлено на {now}</i>\n\n"
            f"<b>📈 Показатели за сегодня:</b>\n"
            f"  • Поступившие заказы: <b>{stats.orders_today_count} шт</b>\n"
            f"  • Выручка за сегодня: <b>{stats.revenue_today:,.2f} USD</b>\n"
            f"  • Чистая прибыль (приблиз.): <b>{stats.profit_today:,.2f} USD</b>\n\n"
            f"<b>💎 Статистика за всё время:</b>\n"
            f"  • Всего поступило денег: <b>{stats.total_revenue:,.2f} USD</b>\n"
            f"  • Продано товаров: <b>{stats.total_grams_sold:,.2f} грамм</b>\n"
            f"  • Общее кол-во заказов: <b>{stats.total_orders_count} шт</b>\n\n"
            f"<b>⏳ Ожидающие действия:</b>\n"
            f"  • Ожидающие пополнения: <b>{stats.pending_topups_count} шт</b>\n"
            f"  • Неподтвержденные заказы: <b>{stats.pending_orders_count} шт</b>\n\n"
            f"<b>📦 Состояние склада и Пользователи:</b>\n"
            f"  • Предупреждение (мало на складе): <b>{stats.low_stock_products_count} шт товаров</b>\n"
            f"  • Активные покупатели в боте: <b>{stats.active_users_count} чел</b>"
        ).replace(",", " ")
    else:
        return (
            f"<b>📊 Tizim Analitikasi va Moliyaviy Grafik</b>\n"
            f"<i>{now} holatiga ko'ra avto-yangilandi</i>\n\n"
            f"<b>📈 Bugungi Ko'rsatkichlar:</b>\n"
            f"  • Tushgan buyurtmalar: <b>{stats.orders_today_count} ta</b>\n"
            f"  • Tushgan tushum: <b>{stats.revenue_today:,.2f} USD</b>\n"
            f"  • Taxminiy sof foyda: <b>{stats.profit_today:,.2f} USD</b>\n\n"
            f"<b>💎 Barcha Vaqtlardagi Statistika:</b>\n"
            f"  • Jami tushgan pullar: <b>{stats.total_revenue:,.2f} USD</b>\n"
            f"  • Ketgan (sotilgan) tovarlar: <b>{stats.total_grams_sold:,.2f} gramm</b>\n"
            f"  • Jami buyurtmalar soni: <b>{stats.total_orders_count} ta</b>\n\n"
            f"<b>⏳ Kutilayotgan harakatlar:</b>\n"
            f"  • Kutilayotgan to'lovlar: <b>{stats.pending_topups_count} ta</b>\n"
            f"  • Tasdiqlanmagan buyurtmalar: <b>{stats.pending_orders_count} ta</b>\n\n"
            f"<b>📦 Ombordagi holat va Foydalanuvchilar:</b>\n"
            f"  • Ogohlantirish (oz qolgan): <b>{stats.low_stock_products_count} ta tovar</b>\n"
            f"  • Faol xaridorlar (botda): <b>{stats.active_users_count} ta</b>"
        ).replace(",", " ")


def format_buyers_message(stats: DashboardStats, lang: str = "uz") -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if lang == "ru":
        lines = [
            f"<b>👥 Список топ покупателей (Кто совершал покупки):</b>",
            f"<i>На момент {now}</i>\n",
        ]
        if not stats.top_buyers:
            lines.append("<i>Пока нет совершённых покупок.</i>")
        else:
            for idx, (u, count, spent, grams) in enumerate(stats.top_buyers, 1):
                user_label = f"@{u.username}" if u.username else u.full_name
                lines.append(
                    f"<b>{idx}. {user_label}</b> (ID: <code>{u.telegram_id}</code>)\n"
                    f"   • Заказы: <b>{count} шт</b> | Количество/Вес: <b>{grams:,.2f} гр</b>\n"
                    f"   • Потраченная сумма: <b>{spent:,.2f} USD</b>\n"
                )
    else:
        lines = [
            f"<b>👥 Top Xaridorlar Ro'yxati (Kimlar tovar olgan):</b>",
            f"<i>{now} holatiga ko'ra</i>\n",
        ]
        if not stats.top_buyers:
            lines.append("<i>Hozircha xaridlar mavjud emas.</i>")
        else:
            for idx, (u, count, spent, grams) in enumerate(stats.top_buyers, 1):
                user_label = f"@{u.username}" if u.username else u.full_name
                lines.append(
                    f"<b>{idx}. {user_label}</b> (ID: <code>{u.telegram_id}</code>)\n"
                    f"   • Buyurtmalar: <b>{count} ta</b> | Soni/Og'irligi: <b>{grams:,.2f} gr</b>\n"
                    f"   • Sarflagan summasi: <b>{spent:,.2f} USD</b>\n"
                )

    return "\n".join(lines).replace(",", " ")


async def show_dashboard(
    target: types.Message | types.CallbackQuery, session: AsyncSession, admin: Admin
):
    service = DashboardService(session)
    stats = await service.get_stats()
    lang = admin.language_code or "uz"
    text = format_dashboard_message(stats, lang=lang)
    keyboard = get_dashboard_keyboard(lang=lang)

    if isinstance(target, types.CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            pass
        await target.answer("Аналитика обновлена!" if lang == "ru" else "Analitika yangilandi!")
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
    lang = admin.language_code or "uz"
    text = format_buyers_message(stats, lang=lang)
    keyboard = get_buyers_keyboard(lang=lang)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("Список покупателей обновлен!" if lang == "ru" else "Xaridorlar ro'yxati yangilandi!")


@router.callback_query(DashboardCallback.filter(F.action == "main_stats"))
async def main_stats_dashboard_handler(
    callback: types.CallbackQuery, session: AsyncSession, admin: Admin
):
    await show_dashboard(callback, session, admin)