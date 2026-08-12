from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, User
from src.shopim.keyboards.inline.admin.topup_management import (
    TopupActionCallback,
    TopupManageCallback,
    get_pending_topups_keyboard,
    get_topup_review_keyboard,
)
from src.shopim.services.topup_management_service import TopupManagementService
from src.shopim.states.admin import TopupRejectionState


from src.shopim.filters import IsAdminFilter


router = Router(name="admin-topup-management-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

ITEMS_PER_PAGE = 5


async def _send_topup_list(
    target: types.Message | types.CallbackQuery, page: int, session: AsyncSession
):
    service = TopupManagementService(session, items_per_page=ITEMS_PER_PAGE)
    result = await service.get_pending_topups(page=page)

    chat_id = target.chat.id if isinstance(target, types.Message) else target.message.chat.id

    if not result.topups:
        text = "⏳ Kutilayotgan balans to'ldirish so'rovlari mavjud emas."
        if isinstance(target, types.CallbackQuery):
            await target.message.answer(text)
            await target.answer()
        else:
            await target.answer(text)
        return

    if isinstance(target, types.Message):
        await target.answer(
            f"Kutilayotgan so'rovlar (Sahifa {result.current_page}/{result.total_pages}):"
        )

    for topup in result.topups:
        text = (
            f"<b>Yangi so'rov!</b>\n\n"
            f"Foydalanuvchi: {topup.user.full_name}\n"
            f"Telegram ID: <code>{topup.user.telegram_id}</code>\n"
            f"Summa: <b>{topup.amount:.2f} so'm</b>\n"
            f"Sana: {topup.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        keyboard = get_topup_review_keyboard(topup_id=topup.id)

        if topup.receipt_file_id:
            await target.bot.send_photo(
                chat_id=chat_id,
                photo=topup.receipt_file_id,
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        else:
            await target.bot.send_message(
                chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="HTML"
            )

    pagination_keyboard = get_pending_topups_keyboard(
        total_pages=result.total_pages, current_page=result.current_page
    )
    if pagination_keyboard:
        await target.bot.send_message(
            chat_id, "Navigatsiya:", reply_markup=pagination_keyboard
        )


@router.message(F.text == "💳 Popolneniya")
async def show_pending_topups_handler(message: types.Message, session: AsyncSession):
    await _send_topup_list(message, 1, session)


@router.callback_query(TopupManageCallback.filter(F.action == "page"))
async def paginate_pending_topups_handler(
    callback: types.CallbackQuery,
    callback_data: TopupManageCallback,
    session: AsyncSession,
):
    await callback.message.delete()
    await _send_topup_list(callback, callback_data.page, session)
    await callback.answer()


@router.callback_query(TopupActionCallback.filter(F.action == "approve"))
async def approve_topup_handler(
    callback: types.CallbackQuery,
    callback_data: TopupActionCallback,
    session: AsyncSession,
    admin: Admin,
    bot: Bot,
):
    service = TopupManagementService(session)
    topup = await service.approve_topup(topup_id=callback_data.topup_id, admin=admin)

    if topup:
        user = await session.get(User, topup.user_id)
        new_caption = (
            f"✅ <b>So'rov tasdiqlandi!</b>\n\n"
            f"Foydalanuvchi: {user.full_name}\n"
            f"Summa: {topup.amount:.2f} so'm\n"
            f"Tasdiqladi: {admin.full_name}"
        )
        await callback.message.edit_caption(caption=new_caption, parse_mode="HTML")

        if user:
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"🎉 Sizning {topup.amount:.2f} so'mlik to'lovingiz tasdiqlandi va balansingizga qo'shildi.",
                )
            except Exception as e:
                print(f"Could not send topup approval notification to user {user.id}: {e}")
    else:
        await callback.message.edit_caption(caption="❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan.")

    await callback.answer("Tasdiqlandi!")


@router.callback_query(TopupActionCallback.filter(F.action == "reject"))
async def reject_topup_start_handler(
    callback: types.CallbackQuery, callback_data: TopupActionCallback, state: FSMContext
):
    await state.set_state(TopupRejectionState.getting_reason)
    await state.update_data(
        topup_id_to_reject=callback_data.topup_id,
        chat_id=callback.message.chat.id,
        message_id_to_edit=callback.message.message_id,
    )
    await callback.message.answer("Iltimos, ushbu to'lovni rad etish sababini yozing.")
    await callback.answer()


@router.message(TopupRejectionState.getting_reason)
async def get_topup_rejection_reason_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, admin: Admin, bot: Bot
):
    reason = message.text
    state_data = await state.get_data()
    topup_id = state_data.get("topup_id_to_reject")
    chat_id = state_data.get("chat_id")
    message_id = state_data.get("message_id_to_edit")

    await state.clear()
    await message.delete()

    service = TopupManagementService(session)
    topup = await service.reject_topup(topup_id=topup_id, admin=admin, reason=reason)

    if topup:
        user = await session.get(User, topup.user_id)
        new_caption = (
            f"❌ <b>So'rov rad etildi!</b>\n\n"
            f"Foydalanuvchi: {user.full_name}\n"
            f"Summa: {topup.amount:.2f} so'm\n"
            f"Rad etdi: {admin.full_name}\n"
            f"Sabab: {reason}"
        )
        try:
            await bot.edit_message_caption(
                chat_id=chat_id, message_id=message_id, caption=new_caption, parse_mode="HTML"
            )
        except Exception:
            await bot.send_message(chat_id, new_caption, parse_mode="HTML")

        if user:
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"Afsuski, sizning {topup.amount:.2f} so'mlik to'lovingiz rad etildi.\nSabab: {reason}",
                )
            except Exception as e:
                print(f"Could not send topup rejection notification to user {user.id}: {e}")
    else:
        try:
            await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption="❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan.",
            )
        except Exception:
            await bot.send_message(chat_id, "❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan.")