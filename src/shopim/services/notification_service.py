from datetime import datetime, timezone

from aiogram import Bot
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Order, OrderStatus, Product, Topup, User
from src.shopim.keyboards.inline.admin.order_management import (
    get_order_approval_keyboard,
)
from src.shopim.keyboards.inline.admin.topup_management import (
    get_topup_review_keyboard,
)
from src.shopim.keyboards.inline.admin.user_management import get_user_approval_keyboard
from src.shopim.services.admin_service import AdminService


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


def get_status_text(status: OrderStatus, locale: str = "uz") -> str:
    status_map = {
        OrderStatus.PENDING_ADMIN: _("⏳ Admin tasdiqlashi kutilmoqda", locale=locale),
        OrderStatus.APPROVED: _("✅ Tasdiqlangan", locale=locale),
        OrderStatus.PACKING: _("📦 Qadoqlanmoqda", locale=locale),
        OrderStatus.OUT_FOR_DELIVERY: _("🚚 Yetkazib berilmoqda", locale=locale),
        OrderStatus.DELIVERED: _("🏁 Yetkazib berilgan", locale=locale),
        OrderStatus.REJECTED: _("❌ Rad etilgan", locale=locale),
        OrderStatus.CANCELLED: _("🚫 Bekor qilingan", locale=locale),
        OrderStatus.REFUNDED: _("💰 Qaytarilgan", locale=locale),
        OrderStatus.DRAFT: _("📝 Qoralama", locale=locale),
    }
    return status_map.get(status, _("Noma'lum", locale=locale))



class NotificationService:
    def __init__(self, bot: Bot, session: AsyncSession):
        self.bot = bot
        self.session = session
        self.admin_service = AdminService(session)

    async def notify_admins(self, text: str, reply_markup=None):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        for admin in active_admins:
            try:
                await self.bot.send_message(
                    admin.telegram_id,
                    text,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            except Exception as e:
                print(f"Could not send notification to admin {admin.telegram_id}: {e}")

    async def notify_admins_of_new_user(self, new_user: User):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        keyboard = get_user_approval_keyboard(user_id=new_user.id)

        for admin in active_admins:
            loc = admin.language_code or "uz"
            text = _(
                "👤 Yangi foydalanuvchi ro'yxatdan o'tdi va tasdiq kutmoqda.\n\n"
                "Foydalanuvchi ID: `{user_id}`\n"
                "Telegram ID: `{telegram_id}`\n"
                "Ism: {full_name}\n"
                "Username: @{username}",
                locale=loc,
            ).format(
                user_id=new_user.id,
                telegram_id=new_user.telegram_id,
                full_name=new_user.full_name,
                username=new_user.username if new_user.username else "N/A",
            )
            try:
                await self.bot.send_message(
                    admin.telegram_id,
                    text,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"Could not send notification to admin {admin.telegram_id}: {e}")

    async def notify_admins_of_new_order(self, order: Order):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        user = await self.session.get(User, order.user_id)

        keyboard = get_order_approval_keyboard(order_id=order.id)

        for admin in active_admins:
            loc = admin.language_code or "uz"
            user_name = user.full_name if user else _("Noma'lum", locale=loc)
            so_m = _("so'm", locale=loc)
            text = _(
                "🛒 Yangi buyurtma keldi!\n\n"
                "Buyurtma №: <b>{order_number}</b>\n"
                "Foydalanuvchi: {user_name}\n"
                "Summa: <b>{total_amount:.2f} {so_m}</b>\n"
                "Sana: {created_at}",
                locale=loc,
            ).format(
                order_number=order.order_number,
                user_name=user_name,
                total_amount=order.total_amount,
                so_m=so_m,
                created_at=order.created_at.strftime("%Y-%m-%d %H:%M"),
            )
            try:
                await self.bot.send_message(
                    admin.telegram_id, text, reply_markup=keyboard, parse_mode="HTML"
                )
            except Exception as e:
                print(f"Could not send new order notification to admin {admin.telegram_id}: {e}")

    async def notify_admins_of_new_topup(self, topup: Topup):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        user = await self.session.get(User, topup.user_id)
        keyboard = get_topup_review_keyboard(topup_id=topup.id)

        for admin in active_admins:
            loc = admin.language_code or "uz"
            user_name = user.full_name if user else _("Noma'lum", locale=loc)
            so_m = _("so'm", locale=loc)
            text = _(
                "💳 Yangi balans to'ldirish so'rovi!\n\n"
                "Foydalanuvchi: {user_name}\n"
                "Summa: <b>{amount:.2f} {so_m}</b>\n"
                "Sana: {created_at}",
                locale=loc,
            ).format(
                user_name=user_name,
                amount=topup.amount,
                so_m=so_m,
                created_at=topup.created_at.strftime("%Y-%m-%d %H:%M"),
            )
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
                print(f"Could not send new topup notification to admin {admin.telegram_id}: {e}")

    async def notify_user_of_delivery_status_change(self, order: Order):
        user = await self.session.get(User, order.user_id)
        if not user:
            return

        user_loc = user.language_code or "uz"
        new_status_text = get_status_text(order.status, locale=user_loc)
        text = _(
            "Sizning №{order_number} buyurtmangiz holati o'zgardi.\n\n"
            "Yangi holat: <b>{new_status_text}</b>",
            locale=user_loc,
        ).format(order_number=order.order_number, new_status_text=new_status_text)

        try:
            await self.bot.send_message(user.telegram_id, text, parse_mode="HTML")
        except Exception as e:
            print(f"Could not send delivery status update to user {user.id} for order {order.id}: {e}")

    async def notify_admins_of_deadline_issue(self, order: Order, issue_type: str):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins:
            return

        for admin in active_admins:
            loc = admin.language_code or "uz"
            if issue_type == "LATE":
                issue_text = _("KECHIKMOQDA", locale=loc)
                details = _(
                    "Belgilangan vaqt ({time}) o'tib ketdi.", locale=loc
                ).format(time=order.delivery_deadline.strftime("%H:%M"))
            elif issue_type == "WARNING":
                minutes_left = round(
                    (order.delivery_deadline - datetime.now(timezone.utc)).total_seconds() / 60
                )
                issue_text = _("MUDDAT YAQINLASHMOQDA", locale=loc)
                details = _(
                    "Yetkazib berishga ~{minutes} daqiqa qoldi.", locale=loc
                ).format(minutes=int(minutes_left))
            else:
                continue

            text = _(
                "❗️ <b>DIQQAT: {issue_text}</b>\n\n"
                "Buyurtma №: <b>{order_number}</b>\n"
                "Foydalanuvchi: {full_name}\n"
                "Holati: {status}\n"
                "Deadline: {deadline}\n\n"
                "{details}",
                locale=loc,
            ).format(
                issue_text=issue_text,
                order_number=order.order_number,
                full_name=order.user.full_name,
                status=get_status_text(order.status, locale=loc),
                deadline=order.delivery_deadline.strftime("%Y-%m-%d %H:%M"),
                details=details,
            )

            try:
                await self.bot.send_message(admin.telegram_id, text, parse_mode="HTML")
            except Exception as e:
                print(f"Could not send deadline notification to admin {admin.telegram_id}: {e}")

    async def notify_admins_of_low_stock(self, products: list[Product]):
        active_admins = await self.admin_service.get_all_active_admins()
        if not active_admins or not products:
            return

        for admin in active_admins:
            loc = admin.language_code or "uz"
            product_lines = [
                f"  - {p.name}: <b>{p.stock_grams} gr</b> ({_('Chegara', locale=loc)}: {p.low_stock_threshold_grams} gr)"
                for p in products
            ]
            product_list_str = "\n".join(product_lines)

            text = _(
                "⚠️ <b>DIQQAT: Mahsulotlar kam qolmoqda!</b>\n\n"
                "Quyidagi mahsulotlar belgilangan miqdordan kam qolgan:\n"
                "{product_list_str}",
                locale=loc,
            ).format(product_list_str=product_list_str)

            try:
                await self.bot.send_message(admin.telegram_id, text, parse_mode="HTML")
            except Exception as e:
                print(f"Could not send low stock notification to admin {admin.telegram_id}: {e}")