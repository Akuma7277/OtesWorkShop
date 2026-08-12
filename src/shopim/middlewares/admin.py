from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.models import Admin, AdminRole
from src.shopim.db.repositories.admin_repository import AdminRepository


class AdminAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        if session is None:
            data["admin"] = None
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            data["admin"] = None
            return await handler(event, data)

        admin_repo = AdminRepository(session)
        admin = await admin_repo.get_by_telegram_id(user.id)

        if not admin:
            settings = get_settings()
            count_stmt = select(func.count(Admin.id))
            admin_count = (await session.execute(count_stmt)).scalar() or 0

            # Auto-promote if user is in SUPER_ADMIN_IDS or if 0 admins exist
            if (user.id in settings.super_admins_list) or (admin_count == 0):
                admin = Admin(
                    telegram_id=user.id,
                    full_name=user.full_name or "Super Admin",
                    role=AdminRole.SUPER_ADMIN,
                    is_active=True,
                )
                session.add(admin)
                await session.commit()
                await session.refresh(admin)

        data["admin"] = admin
        return await handler(event, data)
