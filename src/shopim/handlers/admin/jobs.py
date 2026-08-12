from datetime import datetime, timedelta, timezone

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aiogram.utils.i18n import gettext as _

from src.shopim.db.repositories.order_repository import OrderRepository
from src.shopim.db.repositories.product_repository import ProductRepository
from src.shopim.services.notification_service import NotificationService

# This is a simple in-memory cache to prevent spamming notifications for the same issue.
# A more robust solution for multi-worker environments would use Redis.
# Key: (order_id, issue_type), Value: timestamp
notified_orders_cache = {}
CACHE_EXPIRATION_MINUTES = 120  # 2 hours


def _cleanup_cache():
    """Removes old entries from the cache to prevent memory leaks."""
    expiration_time = datetime.now(timezone.utc) - timedelta(
        minutes=CACHE_EXPIRATION_MINUTES
    )
    keys_to_delete = [
        key for key, ts in notified_orders_cache.items() if ts < expiration_time
    ]
    for key in keys_to_delete:
        del notified_orders_cache[key]


async def check_delivery_deadlines(
    bot: Bot, session_maker: async_sessionmaker[AsyncSession]
):
    """
    Checks for orders with approaching or passed deadlines and notifies admins.
    This job is intended to be run every minute by a scheduler.
    """
    _cleanup_cache()

    async with session_maker() as session:
        order_repo = OrderRepository(session)
        notification_service = NotificationService(bot, session)

        in_progress_orders = await order_repo.get_in_progress_orders_with_deadline()
        now = datetime.now(timezone.utc)

        for order in in_progress_orders:
            deadline = order.delivery_deadline
            if not deadline:
                continue

            if now >= deadline:
                cache_key = (order.id, "LATE")
                if cache_key not in notified_orders_cache:
                    await notification_service.notify_admins_of_deadline_issue(order, "LATE")
                    notified_orders_cache[cache_key] = now
                continue

            warning_time = deadline - timedelta(minutes=15)
            if warning_time <= now < deadline:
                cache_key = (order.id, "WARNING")
                if cache_key not in notified_orders_cache:
                    await notification_service.notify_admins_of_deadline_issue(order, "WARNING")
                    notified_orders_cache[cache_key] = now
                    

async def check_low_stock_products(
    bot: Bot, session_maker: async_sessionmaker[AsyncSession]
):
    """
    Checks for low-stock products and notifies admins.
    This job is intended to be run periodically (e.g., every hour).
    """
    notification_interval = timedelta(hours=24)  # Notify once every 24 hours for the same product

    async with session_maker() as session:
        product_repo = ProductRepository(session)
        notification_service = NotificationService(bot, session)

        products_to_notify = await product_repo.get_low_stock_products_to_notify(
            notification_interval
        )

        if not products_to_notify:
            return

        await notification_service.notify_admins_of_low_stock(products_to_notify)

        # Update the notification timestamp for the notified products
        now = datetime.now(timezone.utc)
        for product in products_to_notify:
            product.last_low_stock_notified_at = now

        await session.commit()