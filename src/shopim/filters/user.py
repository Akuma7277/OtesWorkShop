from typing import Optional
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from src.shopim.db.models import User, UserStatus


class IsApprovedUserFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, user: Optional[User] = None) -> bool:
        return user is not None and user.status == UserStatus.APPROVED
