# ruff: noqa: D101, D102, D103, D104, D105, D107
from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Product
from src.shopim.db.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def count_all(self) -> int:
        stmt = select(func.count(self.model.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_all_paginated(
        self, offset: int, limit: int
    ) -> Sequence[Product]:
        stmt = (
            select(self.model)
            .order_by(self.model.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id_for_update(self, product_id: int) -> Product | None:
        stmt = (
            select(self.model)
            .where(self.model.id == product_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Product | None:
        stmt = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_low_stock_products_to_notify(
        self, notification_interval
    ) -> Sequence[Product]:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        cutoff = now - notification_interval
        stmt = select(Product).where(
            Product.is_active == True,
            Product.stock_grams <= Product.low_stock_threshold_grams,
            or_(
                Product.last_low_stock_notified_at.is_(None),
                Product.last_low_stock_notified_at <= cutoff,
            ),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


