from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User
from src.shopim.db.repositories.review_repository import ReviewRepository
from src.shopim.filters import IsApprovedUserFilter
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard
from src.shopim.services.notification_service import NotificationService
from src.shopim.states.review import ReviewStates

router = Router(name="user-reviews-router")
router.message.filter(IsApprovedUserFilter())


@router.message(
    F.text.in_({
        "Отзывы", "Otzivlar", "💬 Otzivi", "💬 Отзывы", "💬 Sharhlar", "Sharhlar", "💬 Otzivlar"
    }),
    StateFilter("*"),
)
async def show_reviews_handler(message: types.Message, user: User, session: AsyncSession):
    repo = ReviewRepository(session)
    reviews = await repo.get_approved_reviews(limit=10)

    lines = [_("💬 <b>Mijozlarimiz sharhlari:</b>\n")]
    if reviews:
        for rev in reviews:
            user_label = f"@{rev.user.username}" if (rev.user and rev.user.username) else (rev.user.full_name if rev.user else _("Klient"))
            lines.append(f"👤 <b>{user_label}</b>: \"{rev.text}\"\n")
    else:
        lines.append(_("Hozircha sharhlar mavjud emas. Birinchi bo'ling!\n"))

    builder = InlineKeyboardBuilder()
    builder.button(text=_("✍️ Sharh qoldirish"), callback_data="start_write_review")
    builder.adjust(1)

    await message.answer("\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "start_write_review")
async def start_write_review_handler(callback: types.CallbackQuery, state: FSMContext, user: User):
    await state.set_state(ReviewStates.getting_text)
    builder = InlineKeyboardBuilder()
    builder.button(text=_("⬅️ Orqaga"), callback_data="cancel_write_review")
    text = _("✍️ <b>Sharhingizni yozing:</b>\n\nXizmatimiz haqidagi fikringizni qoldiring.")

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_write_review")
async def cancel_write_review_handler(callback: types.CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    msg = _("Sharh yuborish bekor qilindi.")
    await callback.message.edit_text(msg)
    await callback.answer()


@router.message(ReviewStates.getting_text)
async def process_review_text_handler(
    message: types.Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    bot: Bot,
):
    if not message.text or len(message.text.strip()) < 5:
        err_msg = _("Iltimos, batafsilroq sharh yozing (kamida 5 ta belgi).")
        await message.answer(err_msg)
        return

    repo = ReviewRepository(session)
    review = await repo.create_review(user_id=user.id, text=message.text.strip())
    await state.clear()

    notification_service = NotificationService(bot, session)
    user_label = f"@{user.username}" if user.username else user.full_name

    admin_text = _(
        "📝 <b>Yangi sharh moderatsiyaga keldi!</b>\n\n"
        "👤 Mijoz: <b>{user_label}</b> (ID: {telegram_id})\n"
        "💬 Sharh: <i>\"{review_text}\"</i>"
    ).format(user_label=user_label, telegram_id=user.telegram_id, review_text=review.text)

    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("✅ Tasdiqlash va Kanalga joylash"),
        callback_data=f"approve_rev:{review.id}",
    )
    builder.button(
        text=_("❌ Rad etish"),
        callback_data=f"reject_rev:{review.id}",
    )
    builder.adjust(1)

    await notification_service.notify_admins(admin_text, reply_markup=builder.as_markup())

    success_msg = _("Rahmat! Sharhingiz adminga tekshirish uchun yuborildi.")

    await message.answer(
        success_msg,
        reply_markup=get_user_main_keyboard(),
    )
