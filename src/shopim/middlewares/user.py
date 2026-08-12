from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User, UserStatus
from src.shopim.db.repositories.user_repository import UserRepository


class UserAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        if session is None:
            data["user"] = None
            return await handler(event, data)

        telegram_user = data.get("event_from_user")
        if telegram_user is None:
            data["user"] = None
            return await handler(event, data)

        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(telegram_user.id)

        if not user:
            # Auto-create and auto-approve user
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                full_name=telegram_user.full_name or "Foydalanuvchi",
                address="Toshkent",
                age=20,
                status=UserStatus.APPROVED,
                language_code=telegram_user.language_code or "uz",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif user.status == UserStatus.PENDING:
            user.status = UserStatus.APPROVED
            await session.commit()
            await session.refresh(user)

        data["user"] = user
        return await handler(event, data)
