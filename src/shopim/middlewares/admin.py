from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.repositories.admin_repository import AdminRepository

class AdminAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        user = data.get("event_from_user")
        
        if user is None:
            data["admin"] = None
            return await handler(event, data)
            
        admin_repo = AdminRepository(session)
        admin = await admin_repo.get_by_telegram_id(user.id)
        
        data["admin"] = admin
        
        return await handler(event, data)
