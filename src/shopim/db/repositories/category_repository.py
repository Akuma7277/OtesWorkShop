# ruff: noqa: D101, D102, D103, D104, D105, D107
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Category
from src.shopim.db.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def count_all_active(self) -> int:
        stmt = select(func.count(self.model.id)).where(self.model.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_all_active_paginated(
        self, offset: int, limit: int
    ) -> Sequence[Category]:
        stmt = (
            select(self.model)
            .where(self.model.is_active == True)
            .order_by(self.model.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

