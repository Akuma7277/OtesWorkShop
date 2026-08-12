from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
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
    lang = user.language_code or "ru"

    if lang == "uz":
        lines = ["💬 <b>Mijozlarimiz sharhlari:</b>\n"]
        if reviews:
            for rev in reviews:
                user_label = f"@{rev.user.username}" if (rev.user and rev.user.username) else (rev.user.full_name if rev.user else "Klient")
                lines.append(f"👤 <b>{user_label}</b>: \"{rev.text}\"\n")
        else:
            lines.append("Hozircha sharhlar mavjud emas. Birinchi bo'ling!\n")
        write_btn_text = "✍️ Sharh qoldirish"
    else:
        lines = ["💬 <b>Отзывы наших клиентов:</b>\n"]
        if reviews:
            for rev in reviews:
                user_label = f"@{rev.user.username}" if (rev.user and rev.user.username) else (rev.user.full_name if rev.user else "Клиент")
                lines.append(f"👤 <b>{user_label}</b>: \"{rev.text}\"\n")
        else:
            lines.append("Пока нет опубликованных отзывов. Будьте первыми!\n")
        write_btn_text = "✍️ Оставить отзыв"

    builder = InlineKeyboardBuilder()
    builder.button(text=write_btn_text, callback_data="start_write_review")
    builder.adjust(1)

    await message.answer("\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "start_write_review")
async def start_write_review_handler(callback: types.CallbackQuery, state: FSMContext, user: User):
    await state.set_state(ReviewStates.getting_text)
    lang = user.language_code or "ru"
    builder = InlineKeyboardBuilder()
    if lang == "uz":
        builder.button(text="⬅️ Orqaga", callback_data="cancel_write_review")
        text = "✍️ <b>Sharhingizni yozing:</b>\n\nXizmatimiz haqidagi fikringizni qoldiring."
    else:
        builder.button(text="⬅️ Назад", callback_data="cancel_write_review")
        text = "✍️ <b>Напишите ваш отзыв:</b>\n\nПоделитесь вашим впечатлением о нашей работе."

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_write_review")
async def cancel_write_review_handler(callback: types.CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    lang = user.language_code or "ru"
    msg = "Sharh yuborish bekor qilindi." if lang == "uz" else "Отправка отзыва отменена."
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
    lang = user.language_code or "ru"
    if not message.text or len(message.text.strip()) < 5:
        err_msg = "Iltimos, batafsilroq sharh yozing (kamida 5 ta belgi)." if lang == "uz" else "Пожалуйста, напишите более подробный отзыв (минимум 5 символов)."
        await message.answer(err_msg)
        return

    repo = ReviewRepository(session)
    review = await repo.create_review(user_id=user.id, text=message.text.strip())
    await state.clear()

    notification_service = NotificationService(bot, session)
    user_label = f"@{user.username}" if user.username else user.full_name

    admin_text = (
        f"📝 <b>Yangi sharh moderatsiyaga keldi! / Новый отзыв на модерацию!</b>\n\n"
        f"👤 Mijoz: <b>{user_label}</b> (ID: {user.telegram_id})\n"
        f"💬 Sharh: <i>\"{review.text}\"</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Tasdiqlash va Kanalga joylash",
        callback_data=f"approve_rev:{review.id}",
    )
    builder.button(
        text="❌ Rad etish",
        callback_data=f"reject_rev:{review.id}",
    )
    builder.adjust(1)

    await notification_service.notify_admins(admin_text, reply_markup=builder.as_markup())

    success_msg = (
        "Rahmat! Sharhingiz adminga tekshirish uchun yuborildi."
        if lang == "uz"
        else "Спасибо! Ваш отзыв отправлен администратору на проверку."
    )

    await message.answer(
        success_msg,
        reply_markup=get_user_main_keyboard(lang),
    )
