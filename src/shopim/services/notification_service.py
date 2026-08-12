from datetime import datetime, timezone

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.services.admin_service import AdminService
from src.shopim.db.models import Order, OrderStatus, Product, Topup, User
from src.shopim.keyboards.inline.admin.user_management import get_user_approval_keyboard
from src.shopim.keyboards.inline.admin.order_management import (
    get_order_approval_keyboard,
)
from src.shopim.keyboards.inline.admin.topup_management import (
    get_topup_review_keyboard,
)

ORDER_STATUS_MAP = {
    OrderStatus.PENDING_ADMIN: "⏳ Admin tasdiqlashi kutilmoqda",
    OrderStatus.APPROVED: "✅ Tasdiqlangan",
    OrderStatus.PACKING: "📦 Qadoqlanmoqda",
    OrderStatus.OUT_FOR_DELIVERY: "🚚 Yetkazib berilmoqda",
    OrderStatus.DELIVERED: "🏁 Yetkazib berilgan",
    OrderStatus.REJECTED: "❌ Rad etilgan",
    OrderStatus.CANCELLED: "🚫 Bekor qilingan",
    OrderStatus.REFUNDED: "💰 Qaytarilgan",
    OrderStatus.DRAFT: "📝 Qoralama",
}


class NotificationService:
    def __init__(self, bot: Bot, session: AsyncSession):
        self.bot = bot
        self.session = session
        self.admin_service = AdminService(session)

    async def notify_admins_of_new_user(self, new_user: User):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        text = (
            f"👤 Yangi foydalanuvchi ro'yxatdan o'tdi va tasdiq kutmoqda.\n\n"
            f"Foydalanuvchi ID: `{new_user.id}`\n"
            f"Telegram ID: `{new_user.telegram_id}`\n"
            f"Ism: {new_user.full_name}\n"
            f"Username: @{new_user.username if new_user.username else 'N/A'}"
        )
        
        keyboard = get_user_approval_keyboard(user_id=new_user.id)
        
        for admin in active_admins:
            try:
                await self.bot.send_message(
                    admin.telegram_id, 
                    text, 
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Log the error, e.g., if bot is blocked by admin
                print(f"Could not send notification to admin {admin.telegram_id}: {e}")

    async def notify_admins_of_new_order(self, order: Order):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        user = await self.session.get(User, order.user_id)
        user_name = user.full_name if user else "Noma'lum"

        text = (
            f"🛒 Yangi buyurtma keldi!\n\n"
            f"Buyurtma №: <b>{order.order_number}</b>\n"
            f"Foydalanuvchi: {user_name}\n"
            f"Summa: <b>{order.total_amount:.2f} so'm</b>\n"
            f"Sana: {order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

        keyboard = get_order_approval_keyboard(order_id=order.id)

        for admin in active_admins:
            try:
                await self.bot.send_message(
                    admin.telegram_id, text, reply_markup=keyboard, parse_mode="HTML"
                )
            except Exception as e:
                print(
                    f"Could not send new order notification to admin {admin.telegram_id}: {e}"
                )

    async def notify_admins_of_new_topup(self, topup: Topup):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        user = await self.session.get(User, topup.user_id)
        user_name = user.full_name if user else "Noma'lum"

        text = (
            f"💳 Yangi balans to'ldirish so'rovi!\n\n"
            f"Foydalanuvchi: {user_name}\n"
            f"Summa: <b>{topup.amount:.2f} so'm</b>\n"
            f"Sana: {topup.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

        keyboard = get_topup_review_keyboard(topup_id=topup.id)

        for admin in active_admins:
            try:
                if topup.receipt_file_id:
                    await self.bot.send_photo(
                        admin.telegram_id,
                        photo=topup.receipt_file_id,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                else:
                    await self.bot.send_message(
                        admin.telegram_id, text, reply_markup=keyboard, parse_mode="HTML"
                    )
            except Exception as e:
                print(
                    f"Could not send new topup notification to admin {admin.telegram_id}: {e}"
                )

    async def notify_user_of_delivery_status_change(self, order: Order):
        user = await self.session.get(User, order.user_id)
        if not user:
            return

        new_status_text = ORDER_STATUS_MAP.get(order.status, "noma'lum")
        text = (
            f"Sizning №{order.order_number} buyurtmangiz holati o'zgardi.\n\n"
            f"Yangi holat: <b>{new_status_text}</b>"
        )

        try:
            await self.bot.send_message(user.telegram_id, text, parse_mode="HTML")
        except Exception as e:
            print(
                f"Could not send delivery status update to user {user.id} for order {order.id}: {e}"
            )

    async def notify_admins_of_deadline_issue(self, order: Order, issue_type: str):
        """Notifies admins about an order deadline issue (WARNING or LATE)."""
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        if issue_type == "LATE":
            issue_text = "KECHIKMOQDA"
            details = f"Belgilangan vaqt ({order.delivery_deadline.strftime('%H:%M')}) o'tib ketdi."
        elif issue_type == "WARNING":
            minutes_left = round(
                (order.delivery_deadline - datetime.now(timezone.utc)).total_seconds() / 60
            )
            issue_text = "MUDDAT YAQINLASHMOQDA"
            details = f"Yetkazib berishga ~{int(minutes_left)} daqiqa qoldi."
        else:
            return

        text = (
            f"❗️ <b>DIQQAT: {issue_text}</b>\n\n"
            f"Buyurtma №: <b>{order.order_number}</b>\n"
            f"Foydalanuvchi: {order.user.full_name}\n"
            f"Holati: {ORDER_STATUS_MAP.get(order.status, 'Nomalum')}\n"
            f"Deadline: {order.delivery_deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"{details}"
        )

        for admin in active_admins:
            try:
                await self.bot.send_message(admin.telegram_id, text, parse_mode="HTML")
            except Exception as e:
                print(f"Could not send deadline notification to admin {admin.telegram_id}: {e}")

    async def notify_admins_of_low_stock(self, products: list[Product]):
        """Sends a consolidated low-stock notification to all admins."""
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins or not products:
            return

        product_lines = [
            f"  - {p.name}: <b>{p.stock_grams} gr</b> (Chegara: {p.low_stock_threshold_grams} gr)"
            for p in products
        ]
        product_list_str = "\n".join(product_lines)

        text = (
            f"⚠️ <b>DIQQAT: Mahsulotlar kam qolmoqda!</b>\n\n"
            f"Quyidagi mahsulotlar belgilangan miqdordan kam qolgan:\n"
            f"{product_list_str}"
        )

        for admin in active_admins:
            try:
                await self.bot.send_message(admin.telegram_id, text, parse_mode="HTML")
            except Exception as e:
                print(f"Could not send low stock notification to admin {admin.telegram_id}: {e}")