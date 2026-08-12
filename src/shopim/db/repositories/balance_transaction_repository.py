from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import BalanceTransaction


class BalanceTransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_paginated_for_user(
        self, user_id: int, offset: int, limit: int
    ) -> Sequence[BalanceTransaction]:
        stmt = (
            select(BalanceTransaction)
            .where(BalanceTransaction.user_id == user_id)
            .order_by(BalanceTransaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_for_user(self, user_id: int) -> int:
        stmt = select(func.count(BalanceTransaction.id)).where(
            BalanceTransaction.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()