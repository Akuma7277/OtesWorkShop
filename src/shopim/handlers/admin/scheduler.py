from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .jobs import check_delivery_deadlines, check_low_stock_products


def setup_scheduler(bot: Bot, session_maker: async_sessionmaker[AsyncSession]):
    """Initializes and starts the APScheduler."""
    scheduler = AsyncIOScheduler(timezone="UTC")

    # Run deadline checker every minute as per the technical specification.
    scheduler.add_job(
        check_delivery_deadlines,
        "interval",
        minutes=1,
        args=[bot, session_maker],
        id="check_delivery_deadlines_job",
    )

    # Run low stock checker every hour.
    scheduler.add_job(
        check_low_stock_products,
        "interval",
        hours=1,
        args=[bot, session_maker],
        id="check_low_stock_products_job",
    )

    scheduler.start()
    return scheduler