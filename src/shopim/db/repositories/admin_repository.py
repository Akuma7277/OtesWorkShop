# ruff: noqa: D101, D102, D103, D104, D105, D107
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin
from src.shopim.db.repositories.base_repository import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Admin)

    async def get_by_telegram_id(self, telegram_id: int) -> Admin | None:
        stmt = select(self.model).where(
            self.model.telegram_id == telegram_id, self.model.is_active == True
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
