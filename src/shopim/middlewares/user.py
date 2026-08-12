from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.repositories.user_repository import UserRepository

class UserAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        telegram_user = data.get("event_from_user")
        
        if telegram_user is None:
            data["user"] = None
            return await handler(event, data)
            
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(telegram_user.id)
        
        data["user"] = user
        
        return await handler(event, data)
