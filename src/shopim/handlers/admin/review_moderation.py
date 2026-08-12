from aiogram import Bot, F, Router, types
from aiogram.utils.i18n import gettext as _
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
    review = await repo.get_by_id_with_user(review_id)

    if not review:
        await callback.answer(_("Sharh topilmadi."), show_alert=True)
        return

    settings_service = SettingsService(session)
    settings = await settings_service.get_bot_settings()

    channel_msg_id = None
    channel_id = settings.reviews_channel_id.strip()

    posted_to_channel = False
    if channel_id:
        try:
            user_label = (
                f"@{review.user.username}"
                if (review.user and review.user.username)
                else (review.user.full_name if review.user else _("Klient"))
            )
            channel_text = _(
                "💬 <b>Mijozdan yangi sharh!</b>\n\n"
                "👤 Mijoz: <b>{user_label}</b>\n"
                "⭐️ Baho: ⭐️⭐️⭐️⭐️⭐️\n"
                "📝 <i>\"{text}\"</i>"
            ).format(user_label=user_label, text=review.text)
            posted_msg = await bot.send_message(
                chat_id=channel_id, text=channel_text, parse_mode="HTML"
            )
            channel_msg_id = posted_msg.message_id
            posted_to_channel = True
        except Exception as e:
            print(f"Error posting review to channel {channel_id}: {e}")

    await repo.update_review_status(
        review_id=review_id,
        status=ReviewStatus.APPROVED,
        channel_message_id=channel_msg_id,
    )

    # Notify user that their review was approved
    if review.user:
        try:
            user_loc = review.user.language_code or "uz"
            await bot.send_message(
                chat_id=review.user.telegram_id,
                text=_("🎉 <b>Sharhingiz muvaffaqiyatli tasdiqlandi va e'lon qilindi!</b> Ishonchingiz uchun rahmat.", locale=user_loc),
                parse_mode="HTML",
            )
        except Exception:
            pass

    status_text = (
        _("✅ <b>Sharh №{review_id} tasdiqlandi va kanalga joylandi!</b>").format(review_id=review_id)
        if posted_to_channel
        else _("✅ <b>Sharh №{review_id} tasdiqlandi!</b>\n⚠️ <i>Otzivlar kanali sozlamalarda biriktirilmagan.</i>").format(review_id=review_id)
    )

    await callback.message.edit_text(
        status_text,
        parse_mode="HTML",
    )
    await callback.answer(_("Sharh tasdiqlandi!"))


@router.callback_query(F.data.startswith("reject_rev:"))
async def reject_review_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
):
    review_id = int(callback.data.split(":")[1])
    repo = ReviewRepository(session)
    await repo.update_review_status(review_id=review_id, status=ReviewStatus.REJECTED)

    await callback.message.edit_text(
        _("❌ <b>Sharh №{review_id} rad etildi.</b>").format(review_id=review_id),
        parse_mode="HTML",
    )
    await callback.answer(_("Sharh rad etildi."))
