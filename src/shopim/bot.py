import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio.client import Redis

from src.shopim.core.config import get_settings
from src.shopim.handlers import setup_routers
from src.shopim.middlewares.db import DbSessionMiddleware
from src.shopim.middlewares.user import UserAuthMiddleware
from src.shopim.middlewares.admin import AdminAuthMiddleware
from src.shopim.db.models.i18n import LanguageMiddleware
from src.shopim.db.session import create_async_engine, create_session_pool


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

    dp = Dispatcher(storage=storage)

    db_url = settings.db_url
    logger.info(f"Connecting to Database using dialect: {db_url.split('://')[0]}")

    async_engine = create_async_engine(
        url=db_url,
        echo=False,
        pool_pre_ping=True,
    )

    session_pool = create_session_pool(async_engine)

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

    try:
        await dp.start_polling(bot)
    finally:
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
