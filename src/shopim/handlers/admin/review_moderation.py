from aiogram import Bot, F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import ReviewStatus
from src.shopim.db.repositories.review_repository import ReviewRepository
from src.shopim.filters import IsAdminFilter
from src.shopim.services.settings_service import SettingsService

router = Router(name="admin-review-moderation-router")
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data.startswith("approve_rev:"))
async def approve_review_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
    bot: Bot,
):
    review_id = int(callback.data.split(":")[1])
    repo = ReviewRepository(session)
    review = await repo.get_by_id(review_id)

    if not review:
        await callback.answer("Отзыв не найден.", show_alert=True)
        return

    settings_service = SettingsService(session)
    settings = await settings_service.get_bot_settings()

    channel_msg_id = None
    channel_id = settings.reviews_channel_id.strip()

    if channel_id:
        try:
            user_label = (
                f"@{review.user.username}"
                if review.user.username
                else review.user.full_name
            )
            channel_text = (
                f"💬 <b>Новый отзыв от клиента!</b>\n\n"
                f"👤 Клиент: <b>{user_label}</b>\n"
                f"⭐️ Оценка: ⭐️⭐️⭐️⭐️⭐️\n"
                f"📝 <i>\"{review.text}\"</i>"
            )
            posted_msg = await bot.send_message(
                chat_id=channel_id, text=channel_text, parse_mode="HTML"
            )
            channel_msg_id = posted_msg.message_id
        except Exception as e:
            print(f"Error posting review to channel {channel_id}: {e}")

    await repo.update_review_status(
        review_id=review_id,
        status=ReviewStatus.APPROVED,
        channel_message_id=channel_msg_id,
    )

    # Notify user that their review was approved
    try:
        await bot.send_message(
            chat_id=review.user.telegram_id,
            text="🎉 <b>Ваш отзыв успешно одобрен и опубликован!</b> Спасибо за доверие.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await callback.message.edit_text(
        f"✅ <b>Отзыв №{review_id} одобрен и опубликован!</b>",
        parse_mode="HTML",
    )
    await callback.answer("Отзыв одобрен!")


@router.callback_query(F.data.startswith("reject_rev:"))
async def reject_review_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
):
    review_id = int(callback.data.split(":")[1])
    repo = ReviewRepository(session)
    await repo.update_review_status(review_id=review_id, status=ReviewStatus.REJECTED)

    await callback.message.edit_text(
        f"❌ <b>Отзыв №{review_id} отклонен.</b>",
        parse_mode="HTML",
    )
    await callback.answer("Отзыв отклонен.")
