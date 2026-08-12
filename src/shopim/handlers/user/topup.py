from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User, UserStatus
from src.shopim.filters import IsApprovedUserFilter
from src.shopim.keyboards.inline.topup import (
    TopupCallback,
    get_topup_cancellation_keyboard,
)
from src.shopim.services.notification_service import NotificationService
from src.shopim.services.topup_service import TopupService
from src.shopim.states.topup import TopupStates

router = Router(name="user-topup-router")
router.message.filter(IsApprovedUserFilter())
router.callback_query.filter(IsApprovedUserFilter())


# --- Cancellation Handler ---
@router.callback_query(TopupCallback.filter(F.action == "cancel"))
async def cancel_topup_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(_("Balans to'ldirish bekor qilindi."))
    await callback.answer()


# --- Topup Flow ---
@router.message(F.text.in_({"➕ Balans to'ldirish", "➕ Пополнить баланс", "Balans to'ldirish", "Пополнить баланс"}))
async def start_topup_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(TopupStates.getting_amount)
    await message.answer(
        _("Balansni to'ldirish uchun summani kiriting (so'mda):"),
        reply_markup=get_topup_cancellation_keyboard(),
    )


@router.message(TopupStates.getting_amount)
async def get_topup_amount_handler(message: types.Message, state: FSMContext):
    try:
        amount = Decimal(message.text.replace(",", "."))
        if amount <= 1000:  # Example minimum amount
            await message.answer(_("Minimal to'ldirish summasi 1000 so'm."))
            return
    except (InvalidOperation, ValueError):
        await message.answer(_("Xato. Iltimos, summani musbat raqamda kiriting (masalan, 50000)."))
        return

    await state.update_data(amount=str(amount))
    await state.set_state(TopupStates.getting_receipt)
    so_m = _("so'm")
    msg_text = _(
        "Summa qabul qilindi: {amount:.2f} {so_m}.\n\n"
        "Endi to'lovni tasdiqlovchi chek yoki skrinshotni rasm qilib yuboring."
    ).format(amount=amount, so_m=so_m)
    await message.answer(
        msg_text,
        reply_markup=get_topup_cancellation_keyboard(),
    )


@router.message(TopupStates.getting_receipt, F.photo)
async def get_topup_receipt_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User, bot: Bot
):
    receipt_file_id = message.photo[-1].file_id
    state_data = await state.get_data()
    amount = Decimal(state_data.get("amount"))

    await state.clear()

    topup_service = TopupService(session)
    new_topup = await topup_service.create_pending_topup(
        user_id=user.id, amount=amount, receipt_file_id=receipt_file_id
    )

    await message.answer(_("✅ So'rovingiz qabul qilindi. Admin tasdiqlashi bilan balansingizga pul o'tkaziladi."))

    notification_service = NotificationService(bot, session)
    await notification_service.notify_admins_of_new_topup(new_topup)


@router.message(TopupStates.getting_receipt)
async def wrong_receipt_handler(message: types.Message):
    await message.answer(
        _("Iltimos, chekni rasm ko'rinishida yuboring."),
        reply_markup=get_topup_cancellation_keyboard(),
    )