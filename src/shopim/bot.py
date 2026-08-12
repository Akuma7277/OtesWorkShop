import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from redis.asyncio.client import Redis

from src.shopim.core.config import get_settings
from src.shopim.db.models.i18n import LanguageMiddleware
from src.shopim.db.session import create_async_engine, create_session_pool
from src.shopim.handlers import setup_routers
from src.shopim.middlewares.admin import AdminAuthMiddleware
from src.shopim.middlewares.db import DbSessionMiddleware
from src.shopim.middlewares.user import UserAuthMiddleware


async def setup_bot_commands(bot: Bot, settings=None):
    commands = [
        BotCommand(command="start", description="🚀 Botni boshlash / Restart bot"),
        BotCommand(command="menu", description="📋 Asosiy menyu / Main menu"),
        BotCommand(command="app", description="🛍️ Mini App do'kon / Open Mini App"),
        BotCommand(command="admin", description="🛠 Admin paneli / Admin panel"),
        BotCommand(command="user", description="🏠 Foydalanuvchi rejimi / User mode"),
        BotCommand(command="profile", description="👤 Profil / Profile"),
        BotCommand(command="balance", description="💳 Balans to'ldirish / Top up balance"),
        BotCommand(command="cancel", description="🚫 Bekor qilish / Cancel action"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())



async def main():
    settings = get_settings()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting bot...")

    redis_url = settings.get_redis_url
    redis_client = None
    storage = None

    if redis_url:
        try:
            logger.info("Connecting to Redis using REDIS_URL")
            redis_client = Redis.from_url(redis_url)
            storage = RedisStorage(redis=redis_client)
        except Exception as e:
            logger.warning(f"Failed to connect to Redis URL: {e}")

    if not storage:
        host = os.getenv("REDISHOST") or os.getenv("REDIS_HOST")
        if host and host not in ("localhost", "127.0.0.1", "redis"):
            try:
                port = int(os.getenv("REDISPORT") or os.getenv("REDIS_PORT") or settings.redis_port)
                password = os.getenv("REDISPASSWORD") or os.getenv("REDIS_PASSWORD") or None
                logger.info(f"Connecting to Redis at {host}:{port}/{settings.redis_db}")
                redis_client = Redis(
                    host=host,
                    port=port,
                    db=settings.redis_db,
                    password=password,
                )
                storage = RedisStorage(redis=redis_client)
            except Exception as e:
                logger.warning(f"Failed to connect to Redis host: {e}")

    if not storage:
        logger.info("No remote Redis configured. Using MemoryStorage.")
        storage = MemoryStorage()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    await setup_bot_commands(bot, settings)

    dp = Dispatcher(storage=storage)


    db_url = settings.db_url
    logger.info(f"Connecting to Database using dialect: {db_url.split('://')[0]}")

    async_engine = create_async_engine(
        url=db_url,
        echo=False,
        pool_pre_ping=True,
    )

    if "sqlite" in db_url:
        logger.info("Auto-creating SQLite tables...")
        from src.shopim.db.models.all_models import Base
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    session_pool = create_session_pool(async_engine)

    # Seed Tashkent districts as default locations
    async with session_pool() as session:
        from sqlalchemy import select
        from src.shopim.db.models import Category
        stmt = select(Category)
        existing = (await session.execute(stmt)).scalars().all()
        existing_names = {c.name for c in existing}

        tashkent_districts = [
            "Yunusobod",
            "Chilonzor",
            "Mirobod",
            "Mirzo Ulug'bek",
            "Yashnobod",
            "Shayxontohur",
            "Olmazor",
            "Uchtepa",
            "Yakkasaroy",
            "Sergeli",
            "Yangihayot",
            "Bektemir",
        ]

        added = False
        for district in tashkent_districts:
            if district not in existing_names:
                session.add(Category(name=district, is_active=True))
                added = True
        if added:
            await session.commit()

    dp.update.middleware(
        DbSessionMiddleware(session_pool=session_pool)
    )

    dp.update.middleware(
        UserAuthMiddleware()
    )

    dp.update.middleware(
        AdminAuthMiddleware()
    )

    dp.update.middleware(
        LanguageMiddleware()
    )

    setup_routers(dp)

    async def auto_analytics_scheduler():
        while True:
            try:
                await asyncio.sleep(1800)  # Every 30 minutes
                async with session_pool() as session:
                    from src.shopim.handlers.admin.dashboard import format_dashboard_message
                    from src.shopim.services.dashboard_service import DashboardService
                    from src.shopim.services.notification_service import NotificationService

                    service = DashboardService(session)
                    stats = await service.get_stats()
                    report_text = f"🔄 <b>[AVTO-ANALITIKA - HAR 30 MINUT]</b>\n\n" + format_dashboard_message(stats)

                    notification_service = NotificationService(bot, session)
                    await notification_service.notify_admins(report_text)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto_analytics_scheduler: {e}")

    analytics_task = asyncio.create_task(auto_analytics_scheduler())

    try:
        await dp.start_polling(bot)
    finally:
        analytics_task.cancel()
        await bot.session.close()
        if redis_client:
            await redis_client.close()
        await async_engine.dispose()
        logger.info("Bot stopped.")


def run():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("Bot stopped by user.")


if __name__ == "__main__":
    run()
