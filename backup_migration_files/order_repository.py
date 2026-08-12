from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shopim.db.models import Order, OrderStatus, User


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_paginated_for_user(
        self, user_id: int, offset: int, limit: int
    ) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_for_user(self, user_id: int) -> int:
        stmt = select(func.count(Order.id)).where(Order.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id_with_items(
        self, order_id: int, user_id: int
    ) -> Order | None:
        """Gets a single order with its items, ensuring it belongs to the user."""
        stmt = select(Order).where(Order.id == order_id, Order.user_id == user_id).options(
            selectinload(Order.items)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_in_progress_orders_with_deadline(self) -> Sequence[Order]:
        """Gets all orders that are currently in progress and have a deadline."""
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
                Order.delivery_deadline.is_not(None),
            )
            .options(selectinload(Order.user))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_paginated(
        self, query: str, offset: int, limit: int
    ) -> Sequence[Order]:
        search_query = f"%{query}%"
        try:
            telegram_id_query = int(query)
        except ValueError:
            telegram_id_query = -1

        stmt = (
            select(Order)
            .join(User, User.id == Order.user_id)
            .where(
                or_(
                    Order.order_number.ilike(search_query),
                    User.full_name.ilike(search_query),
                    User.telegram_id == telegram_id_query,
                )
            )
            .order_by(Order.created_at.desc())
            .options(selectinload(Order.user))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_search(self, query: str) -> int:
        search_query = f"%{query}%"
        try:
            telegram_id_query = int(query)
        except ValueError:
            telegram_id_query = -1

        stmt = select(func.count(Order.id)).join(User, User.id == Order.user_id).where(
            or_(
                Order.order_number.ilike(search_query),
                User.full_name.ilike(search_query),
                User.telegram_id == telegram_id_query,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id_with_details(self, order_id: int) -> Order | None:
        """Gets a single order with its items and user, for admin view."""
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items), selectinload(Order.user))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()