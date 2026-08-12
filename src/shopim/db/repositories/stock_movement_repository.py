from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shopim.db.models import StockMovement


class StockMovementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_paginated_movements(
        self, offset: int, limit: int
    ) -> Sequence[StockMovement]:
        stmt = (
            select(StockMovement)
            .order_by(StockMovement.created_at.desc())
            .options(selectinload(StockMovement.product))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_movements(self) -> int:
        stmt = select(func.count(StockMovement.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()