from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> Sequence[Category]:
        stmt = select(Category).where(Category.is_active.is_(True)).order_by(Category.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_active_paginated(
        self, offset: int, limit: int
    ) -> Sequence[Category]:
        stmt = (
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all_active(self) -> int:
        stmt = select(func.count(Category.id)).where(Category.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalar_one()