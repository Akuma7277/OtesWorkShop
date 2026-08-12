from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.models import Order, OrderStatus, User
from src.shopim.filters import IsApprovedUserFilter
from src.shopim.keyboards.inline.language import (
    LanguageCallback,
    get_language_selection_keyboard,
)
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard

router = Router(name="user-profile-router")
router.message.filter(IsApprovedUserFilter())


@router.message(F.text.in_({"Профиль", "Profil", "👤 Profil", "👤 Профиль"}), StateFilter("*"))
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

    lang = user.language_code or "ru"
    if lang == "uz":
        profile_text = (
            f"👤 <b>Sizning profilingiz</b>\n"
            f"🧾 Xaridlar: <b>{total_purchases}</b>\n"
            f"💰 Xaridlar summasi: <b>{total_spent:.2f} USD</b>\n"
            f"👨‍👩‍👧‍👦 Botlardan daromad: <b>0.00 USD</b>\n"
            f"👥 Botlardagi foydalanuvchilar: <b>0</b>\n"
            f"💳 Balans: <b>0.00 USD</b>\n"
            f"🎁 Chegirma: <b>0%</b>\n"
            f"--------------------\n"
            f"📊 Sizning botlaringiz: <b>yo'q</b>"
        )
    else:
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
        reply_markup=get_user_main_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_({"🌐 Сменить язык", "🌐 Tilni o'zgartirish", "Tilni o'zgartirish", "Сменить язык"}), StateFilter("*"))
async def show_language_change_menu(message: types.Message, user: User):
    lang = user.language_code or "ru"
    prompt = (
        "Tilni tanlang / Выберите язык:"
        if lang == "uz"
        else "Выберите язык / Tilni tanlang:"
    )
    await message.answer(
        prompt,
        reply_markup=get_language_selection_keyboard(),
    )


@router.callback_query(LanguageCallback.filter())
async def process_language_change(
    callback: types.CallbackQuery,
    callback_data: LanguageCallback,
    user: User,
    session: AsyncSession,
):
    new_lang = callback_data.code
    user.language_code = new_lang
    await session.commit()

    if new_lang == "uz":
        alert_msg = "Til muvaffaqiyatli O'zbekchaga o'zgartirildi!"
        confirm_text = "🇺🇿 <b>Til o'zgartirildi: O'zbekcha</b>"
    else:
        alert_msg = "Язык успешно изменен на Русский!"
        confirm_text = "🇷🇺 <b>Язык изменен: Русский</b>"

    await callback.answer(alert_msg, show_alert=True)
    await callback.message.edit_text(confirm_text, parse_mode="HTML")
    await callback.message.answer(
        "Menyu:" if new_lang == "uz" else "Главное меню:",
        reply_markup=get_user_main_keyboard(new_lang),
    )


@router.message(F.text.in_({"Работа! ПЛАТИМ ДОХУЯ!", "Работа!", "Ish!", "💼 Работа!", "💼 Ish! YUQORI MAOSH!"}), StateFilter("*"))
async def show_job_handler(message: types.Message, user: User):
    settings = get_settings()
    lang = user.language_code or "ru"
    if lang == "uz":
        job_text = (
            f"💼 <b>Ish! YUQORI MAOSH!</b>\n\n"
            f"Kuryerlar, qadoqlovchilar va omborchilar talab qilinadi!\n"
            f"Yuqori maosh, moslashuvchan grafik va to'liq maxfiylik.\n\n"
            f"Operator bilan bog'lanish: {settings.operator_contact}"
        )
    else:
        job_text = (
            f"💼 <b>Работа! ПЛАТИМ ДОХУЯ!</b>\n\n"
            f"Требуются курьеры, фасовщики и складские работники!\n"
            f"Высокая оплата, гибкий график и полная анонимность.\n\n"
            f"Для связи с оператором: {settings.operator_contact}"
        )
    await message.answer(
        job_text,
        reply_markup=get_user_main_keyboard(lang),
        parse_mode="HTML",
    )
