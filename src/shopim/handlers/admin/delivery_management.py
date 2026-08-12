from typing import Optional

from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, OrderStatus
from src.shopim.services.notification_service import ORDER_STATUS_MAP
from src.shopim.keyboards.inline.admin.delivery_management import (
    DeliveryActionCallback,
    get_delivery_action_keyboard,
)
from src.shopim.services.delivery_service import DeliveryService
from src.shopim.services.notification_service import NotificationService


class IsAdminFilter:
    def __call__(self, admin: Optional[Admin]) -> bool:
        return admin is not None


router = Router(name="admin-delivery-management-router")
router.callback_query.filter(IsAdminFilter())


@router.callback_query(DeliveryActionCallback.filter())
async def set_delivery_status_handler(
    callback: CallbackQuery,
    callback_data: DeliveryActionCallback,
    session: AsyncSession,
    admin: Admin,
    bot: Bot,
):
    service = DeliveryService(session)
    new_status = OrderStatus[callback_data.status]

    updated_order = await service.update_delivery_status(
        order_id=callback_data.order_id, new_status=new_status, admin=admin
    )

    if updated_order:
        await callback.answer(_("Holat o'zgartirildi: {status_name}").format(status_name=new_status.name))

        # Eager load relationships for display
        await session.refresh(updated_order, attribute_names=["items", "user"])

        # Notify user
        notification_service = NotificationService(bot, session)
        await notification_service.notify_user_of_delivery_status_change(updated_order)

        # Refresh the admin's view
        items_text = "\n".join(
            [
                f"  - {item.product_name_snapshot}: {item.grams} gr. = {item.subtotal:.2f} so'm"
                for item in updated_order.items
            ]
        )

        text = (
            _("<b>Buyurtma №{order_number}</b>\n\n"
              "<b>Foydalanuvchi:</b> {user_full_name} (ID: <code>{user_telegram_id}</code>)\n"
              "<b>Holati:</b> {status}\n"
              "<b>Sana:</b> {created_at}\n"
              "<b>Jami summa:</b> {total_amount:.2f} so'm\n"
              "<b>Yetkazish manzili:</b> {delivery_address}\n\n"
              "<b>Mahsulotlar:</b>\n{items_text}").format(
                order_number=updated_order.order_number, user_full_name=updated_order.user.full_name, user_telegram_id=updated_order.user.telegram_id,
                status=ORDER_STATUS_MAP.get(updated_order.status, "Nomalum"), created_at=updated_order.created_at.strftime('%Y-%m-%d %H:%M'),
                total_amount=updated_order.total_amount, delivery_address=updated_order.delivery_address, items_text=items_text
            )
        )

        keyboard = get_delivery_action_keyboard(
            order=updated_order, page=callback_data.page
        )
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore

    else:
        await callback.answer(
            _("Holatni o'zgartirib bo'lmadi. Buyurtma holati mos kelmasligi mumkin."),
            show_alert=True,
        )