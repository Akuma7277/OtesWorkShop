from typing import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_paginated_by_category(
        self, category_id: int, offset: int, limit: int
    ) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(Product.category_id == category_id, Product.is_active.is_(True))
            .order_by(Product.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_category(self, category_id: int) -> int:
        stmt = (
            select(func.count(Product.id))
            .where(Product.category_id == category_id, Product.is_active.is_(True))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_slug(self, slug: str) -> Product | None:
        stmt = select(Product).where(Product.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, product_id: int) -> Product | None:
        """Gets a product by ID and locks the row for update."""
        stmt = select(Product).where(Product.id == product_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_low_stock_products_to_notify(
        self, notification_interval: timedelta
    ) -> Sequence[Product]:
        """
        Gets products that are low in stock and for which a notification
        has not been sent recently.
        """
        time_ago = datetime.now(timezone.utc) - notification_interval
        stmt = select(Product).where(
            Product.is_active == True,
            Product.stock_grams <= Product.low_stock_threshold_grams,
            or_(
                Product.last_low_stock_notified_at.is_(None),
                Product.last_low_stock_notified_at < time_ago,
            ),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_paginated(
        self, offset: int, limit: int
    ) -> Sequence[Product]:
        stmt = (
            select(Product)
            .order_by(Product.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all(self) -> int:
        stmt = select(func.count(Product.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search_paginated(
        self, query: str, offset: int, limit: int
    ) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(Product.name.ilike(f"%{query}%"), Product.is_active.is_(True))
            .order_by(Product.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_search(self, query: str) -> int:
        stmt = (
            select(func.count(Product.id))
            .where(Product.name.ilike(f"%{query}%"), Product.is_active.is_(True))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()