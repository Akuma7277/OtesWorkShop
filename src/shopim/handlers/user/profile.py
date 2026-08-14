from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.utils.i18n import gettext as _
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

    profile_text = _(
        "👤 <b>Sizning profilingiz</b>\n"
        "🧾 Xaridlar: <b>{total_purchases}</b>\n"
        "💰 Xaridlar summasi: <b>{total_spent:.2f} USD</b>\n"
        "💳 Balans: <b>0.00 USD</b>\n"
        "🎁 Chegirma: <b>0%</b>"
    ).format(total_purchases=total_purchases, total_spent=total_spent)

    await message.answer(
        profile_text,
        reply_markup=get_user_main_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text.in_({"🌐 Сменить язык", "🌐 Tilni o'zgartirish", "Tilni o'zgartirish", "Сменить язык"}), StateFilter("*"))
async def show_language_change_menu(message: types.Message, user: User):
    prompt = _("Tilni tanlang / Выберите язык:")
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
        menu_text = "Asosiy menyu:"
    else:
        alert_msg = "Язык успешно изменен на Русский!"
        confirm_text = "🇷🇺 <b>Язык изменен: Русский</b>"
        menu_text = "Главное меню:"

    await callback.answer(alert_msg, show_alert=True)
    await callback.message.edit_text(confirm_text, parse_mode="HTML")
    await callback.message.answer(
        menu_text,
        reply_markup=get_user_main_keyboard(),
    )


@router.message(F.text.in_({"Работа! ПЛАТИМ ДОХУЯ!", "Работа!", "Ish!", "💼 Работа!", "💼 Ish! YUQORI MAOSH!"}), StateFilter("*"))
async def show_job_handler(message: types.Message, user: User):
    settings = get_settings()
    job_text = _(
        "💼 <b>Ish! YUQORI MAOSH!</b>\n\n"
        "Kuryerlar, qadoqlovchilar va omborchilar talab qilinadi!\n"
        "Yuqori maosh, moslashuvchan grafik va to'liq maxfiylik.\n\n"
        "Operator bilan bog'lanish: <a href=\"{operator}\">Bog'lanish</a>"
    ).format(operator=settings.operator_contact)

    await message.answer(
        job_text,
        reply_markup=get_user_main_keyboard(),
        parse_mode="HTML",
    )
