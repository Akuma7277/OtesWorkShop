from aiogram import F, Router, types
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.models import Order, OrderStatus, User
from src.shopim.filters import IsApprovedUserFilter
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard

router = Router(name="user-profile-router")
router.message.filter(IsApprovedUserFilter())


@router.message(F.text.in_({"Профиль", "Profil", "👤 Profil", "👤 Профиль"}))
async def show_profile_handler(message: types.Message, user: User, session: AsyncSession):
    stmt = (
        select(
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(Order.total_amount), 0).label("total_spent"),
        )
        .where(Order.user_id == user.id)
        .where(Order.status == OrderStatus.DELIVERED)
    )
    result = await session.execute(stmt)
    stats = result.one()
    total_purchases = stats.total_orders
    total_spent = float(stats.total_spent)

    profile_text = (
        f"👤 <b>Ваш профиль</b>\n"
        f"🧾 Покупок: <b>{total_purchases}</b>\n"
        f"💰 Сумма покупок: <b>{total_spent:.2f} USD</b>\n"
        f"👨‍👩‍👧‍👦 Доход от ботов: <b>0.00 USD</b>\n"
        f"👥 Пользователей в ботах: <b>0</b>\n"
        f"💳 Баланс: <b>0.00 USD</b>\n"
        f"🎁 Скидка: <b>0%</b>\n"
        f"--------------------\n"
        f"📊 Ваши боты: <b>нет</b>"
    )

    await message.answer(
        profile_text,
        reply_markup=get_user_main_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text.in_({"Работа! ПЛАТИМ ДОХУЯ!", "Работа!", "Ish!", "💼 Работа!"}))
async def show_job_handler(message: types.Message):
    settings = get_settings()
    job_text = (
        f"💼 <b>Работа! ПЛАТИМ ДОХУЯ!</b>\n\n"
        f"Требуются курьеры, фасовщики и складские работники!\n"
        f"Высокая оплата, гибкий график и полная анонимность.\n\n"
        f"Для связи с оператором yozing: {settings.operator_contact}"
    )
    await message.answer(
        job_text,
        reply_markup=get_user_main_keyboard(),
        parse_mode="HTML",
    )
