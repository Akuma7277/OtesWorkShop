from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
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
        text = _("⏳ Kutilayotgan balans to'ldirish so'rovlari mavjud emas.")
        if isinstance(target, types.CallbackQuery) and target.message:
            await target.message.answer(text)
            await target.answer()
        elif isinstance(target, types.Message):
            await target.answer(text)
        return

    if isinstance(target, types.Message):
        await target.answer(
            _("Kutilayotgan so'rovlar (Sahifa {current_page}/{total_pages}):").format(current_page=result.current_page, total_pages=result.total_pages)
        )

    for topup in result.topups:
        text = (
            _("<b>Yangi so'rov!</b>\n\n"
              "Foydalanuvchi: {user_full_name}\n"
              "Telegram ID: <code>{user_telegram_id}</code>\n"
              "Summa: <b>{amount:.2f} so'm</b>\n"
              "Sana: {created_at}").format(
                user_full_name=topup.user.full_name, user_telegram_id=topup.user.telegram_id,
                amount=topup.amount, created_at=topup.created_at.strftime('%Y-%m-%d %H:%M')
            )
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
    if pagination_keyboard and hasattr(target, 'bot'):
        await target.bot.send_message(
            chat_id, "Navigatsiya:", reply_markup=pagination_keyboard
        )


from aiogram.filters import StateFilter

@router.message(F.text.in_({"💳 To'lovlar", "💳 Popolneniya", "💳 Пополнения"}), StateFilter("*"))
async def show_pending_topups_handler(message: types.Message, session: AsyncSession):
    await _send_topup_list(message, 1, session)
    

@router.callback_query(TopupManageCallback.filter(F.action == "page"))
async def paginate_pending_topups_handler(
    callback: types.CallbackQuery,
    callback_data: TopupManageCallback,
    session: AsyncSession,
):
    if callback.message:
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
        if user:
            new_caption = (
                _("✅ <b>So'rov tasdiqlandi!</b>\n\n"
                  "Foydalanuvchi: {user_full_name}\n"
                  "Summa: {amount:.2f} so'm\n"
                  "Tasdiqladi: {admin_full_name}").format(user_full_name=user.full_name, amount=topup.amount, admin_full_name=admin.full_name)
            )
            if callback.message:
                await callback.message.edit_caption(caption=new_caption, parse_mode="HTML")

            try:
                await bot.send_message(
                    user.telegram_id,
                    _("🎉 Sizning {amount:.2f} so'mlik to'lovingiz tasdiqlandi va balansingizga qo'shildi.").format(amount=topup.amount),
                )
            except Exception as e:
                print(f"Could not send topup approval notification to user {user.id}: {e}")
    else:
        if callback.message:
            await callback.message.edit_caption(caption=_("❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan."), parse_mode="HTML")

    await callback.answer(_("Tasdiqlandi!"))


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
    if callback.message:
        await callback.message.answer(_("Iltimos, ushbu to'lovni rad etish sababini yozing."))
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
        if user:
            new_caption = (
                _("❌ <b>So'rov rad etildi!</b>\n\n"
                  "Foydalanuvchi: {user_full_name}\n"
                  "Summa: {amount:.2f} so'm\n"
                  "Rad etdi: {admin_full_name}\n"
                  "Sabab: {reason}").format(user_full_name=user.full_name, amount=topup.amount, admin_full_name=admin.full_name, reason=reason)
            )
            try:
                await bot.edit_message_caption(
                    chat_id=chat_id, message_id=message_id, caption=new_caption, parse_mode="HTML"
                )
            except Exception:
                await bot.send_message(chat_id, new_caption, parse_mode="HTML")

            try:
                await bot.send_message(
                    user.telegram_id,
                    _("Afsuski, sizning {amount:.2f} so'mlik to'lovingiz rad etildi.\nSabab: {reason}").format(amount=topup.amount, reason=reason),
                )
            except Exception as e:
                print(f"Could not send topup rejection notification to user {user.id}: {e}")
    else:
        try:
            await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=_("❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan."),
            )
        except Exception:
            if chat_id:
                await bot.send_message(chat_id, _("❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan."))