# ruff: noqa: D101, D102, D103, D104, D105, D107
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shopim.db.models import Topup, TopupStatus
from src.shopim.db.repositories.base_repository import BaseRepository


class TopupRepository(BaseRepository[Topup]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Topup)

    async def get_paginated_pending(
        self, offset: int, limit: int
    ) -> Sequence[Topup]:
        stmt = (
            select(Topup)
            .where(Topup.status == TopupStatus.PENDING)
            .order_by(Topup.created_at.asc())
            .options(selectinload(Topup.user))  # Eager load user data
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_pending(self) -> int:
        stmt = select(func.count(Topup.id)).where(Topup.status == TopupStatus.PENDING)
        result = await self.session.execute(stmt)
        return result.scalar_one()
