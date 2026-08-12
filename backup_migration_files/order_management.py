from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, User
from src.shopim.keyboards.inline.admin.order_management import OrderApprovalCallback
from src.shopim.services.order_management_service import OrderManagementService
from src.shopim.states.admin import OrderRejectionState


class IsAdminFilter:
    def __call__(self, admin: Optional[Admin]) -> bool:
        return admin is not None


router = Router(name="admin-order-management-router")
router.callback_query.filter(IsAdminFilter())
router.message.filter(IsAdminFilter())


@router.callback_query(OrderApprovalCallback.filter(F.action == "approve"))
async def approve_order_handler(
    callback: types.CallbackQuery,
    callback_data: OrderApprovalCallback,
    session: AsyncSession,
    admin: Admin,
    bot: Bot,
):
    service = OrderManagementService(session)
    order = await service.approve_order(order_id=callback_data.order_id, admin=admin)

    if order:
        await callback.message.edit_text(
            f"✅ Buyurtma (№{order.order_number}) {admin.full_name} tomonidan tasdiqlandi."
        )
        user = await session.get(User, order.user_id)
        if user:
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"🎉 Sizning №{order.order_number} buyurtmangiz tasdiqlandi va tez orada qadoqlanadi.",
                )
            except Exception as e:
                print(
                    f"Could not send approval notification to user for order {order.id}: {e}"
                )
    else:
        await callback.message.edit_text(
            "Buyurtma topilmadi yoki allaqachon ko'rib chiqilgan."
        )

    await callback.answer()


@router.callback_query(OrderApprovalCallback.filter(F.action == "reject"))
async def reject_order_start_handler(
    callback: types.CallbackQuery, callback_data: OrderApprovalCallback, state: FSMContext
):
    await state.set_state(OrderRejectionState.getting_reason)
    await state.update_data(
        order_id_to_reject=callback_data.order_id,
        message_id_to_edit=callback.message.message_id,
    )
    await callback.message.answer(
        "Iltimos, ushbu buyurtmani rad etish sababini yozing."
    )
    await callback.answer()


@router.message(OrderRejectionState.getting_reason)
async def get_order_rejection_reason_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
    admin: Admin,
    bot: Bot,
):
    reason = message.text
    state_data = await state.get_data()
    order_id = state_data.get("order_id_to_reject")
    message_id = state_data.get("message_id_to_edit")

    await state.clear()

    service = OrderManagementService(session)
    order = await service.reject_order(order_id=order_id, admin=admin, reason=reason)

    await message.delete()

    if order:
        try:
            await bot.edit_message_text(
                f"❌ Buyurtma (№{order.order_number}) {admin.full_name} tomonidan rad etildi.\nSabab: {reason}",
                chat_id=message.chat.id,
                message_id=message_id,
            )
        except Exception:
            await message.answer(
                f"❌ Buyurtma (№{order.order_number}) {admin.full_name} tomonidan rad etildi.\nSabab: {reason}"
            )

        user = await session.get(User, order.user_id)
        if user:
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"Afsuski, sizning №{order.order_number} buyurtmangiz rad etildi.\nSabab: {reason}\n\nTo'langan summa balansingizga qaytarildi.",
                )
            except Exception as e:
                print(
                    f"Could not send rejection notification to user for order {order.id}: {e}"
                )
    else:
        await message.answer("Buyurtma topilmadi yoki allaqachon ko'rib chiqilgan.")