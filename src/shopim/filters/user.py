from typing import Optional
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from src.shopim.db.models import User


class IsApprovedUserFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, user: Optional[User] = None) -> bool:
        if user is None:
            return True
        status_val = getattr(user, "status", None)
        if status_val is None:
            return True
        status_str = str(status_val.value) if hasattr(status_val, "value") else str(status_val)
        return status_str.upper() != "BLOCKED"
