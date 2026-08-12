from aiogram import Bot, F, Router, types
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


@router.message(F.text.in_({"Отзывы", "Otzivlar", "💬 Otzivi", "💬 Отзывы"}))
async def show_reviews_handler(message: types.Message, session: AsyncSession):
    repo = ReviewRepository(session)
    reviews = await repo.get_approved_reviews(limit=10)

    lines = ["💬 <b>Отзывы наших клиентов:</b>\n"]
    if reviews:
        for rev in reviews:
            user_label = f"@{rev.user.username}" if rev.user.username else rev.user.full_name
            lines.append(f"👤 <b>{user_label}</b>: \"{rev.text}\"\n")
    else:
        lines.append("Пока нет опубликованных отзывов. Будьте первыми!\n")

    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Оставить отзыв", callback_data="start_write_review")
    builder.adjust(1)

    await message.answer("\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "start_write_review")
async def start_write_review_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ReviewStates.getting_text)
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="cancel_write_review")
    await callback.message.edit_text(
        "✍️ <b>Напишите ваш отзыв:</b>\n\nПоделитесь вашим впечатлением о нашей работе.",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_write_review")
async def cancel_write_review_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Отправка отзыва отменена.")
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
        await message.answer("Пожалуйста, напишите более подробный отзыв (минимум 5 символов).")
        return

    repo = ReviewRepository(session)
    review = await repo.create_review(user_id=user.id, text=message.text.strip())
    await state.clear()

    notification_service = NotificationService(bot, session)
    user_label = f"@{user.username}" if user.username else user.full_name

    admin_text = (
        f"📝 <b>Новый отзыв на модерацию!</b>\n\n"
        f"👤 Клиент: <b>{user_label}</b> (ID: {user.telegram_id})\n"
        f"💬 Отзыв: <i>\"{review.text}\"</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Одобрить и опубликовать",
        callback_data=f"approve_rev:{review.id}",
    )
    builder.button(
        text="❌ Отклонить",
        callback_data=f"reject_rev:{review.id}",
    )
    builder.adjust(1)

    await notification_service.notify_admins(admin_text, reply_markup=builder.as_markup())
    await message.answer(
        "Спасибо! Ваш отзыв отправлен администратору на проверку.",
        reply_markup=get_user_main_keyboard(),
    )
