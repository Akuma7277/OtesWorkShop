# ruff: noqa: D101, D102, D103, D104, D105, D107
from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shopim.db.models import Order
from src.shopim.db.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)

    async def count_search(self, query: str) -> int:
        try:
            order_id_query = int(query)
        except ValueError:
            order_id_query = -1

        stmt = select(func.count(Order.id)).where(
            or_(
                Order.order_number.ilike(f"%{query}%"),
                Order.id == order_id_query,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search_paginated(
        self, query: str, offset: int, limit: int
    ) -> Sequence[Order]:
        try:
            order_id_query = int(query)
        except ValueError:
            order_id_query = -1

        stmt = (
            select(Order)
            .where(
                or_(
                    Order.order_number.ilike(f"%{query}%"),
                    Order.id == order_id_query,
                )
            )
            .options(selectinload(Order.user), selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id_with_details(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.items),
                selectinload(Order.delivery_events),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_in_progress_orders_with_deadline(self) -> Sequence[Order]:
        from src.shopim.db.models import OrderStatus
        stmt = (
            select(Order)
            .where(
                Order.status.in_(
                    [
                        OrderStatus.APPROVED,
                        OrderStatus.PACKING,
                        OrderStatus.OUT_FOR_DELIVERY,
                    ]
                ),
                Order.delivery_deadline.isnot(None),
            )
            .options(selectinload(Order.user))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

