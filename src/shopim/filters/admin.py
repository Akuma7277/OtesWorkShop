from typing import Optional
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from src.shopim.db.models import Admin, AdminRole


class IsAdminFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, admin: Optional[Admin] = None) -> bool:
        return admin is not None


class IsSuperAdminFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, admin: Optional[Admin] = None) -> bool:
        return admin is not None and admin.role == AdminRole.SUPER_ADMIN
