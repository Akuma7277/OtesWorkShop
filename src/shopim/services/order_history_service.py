import math
from typing import NamedTuple, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shopim.db.models import Order


class PaginatedUserOrders(NamedTuple):
    orders: Sequence[Order]
    total_pages: int
    current_page: int


class OrderHistoryService:
    def __init__(self, session: AsyncSession, orders_per_page: int = 5):
        self.session = session
        self.orders_per_page = orders_per_page

    async def get_user_orders(self, user_id: int, page: int = 1) -> PaginatedUserOrders:
        total_count = await self._count_user_orders(user_id)
        if total_count == 0:
            return PaginatedUserOrders([], 0, page)

        total_pages = math.ceil(total_count / self.orders_per_page)
        offset = (page - 1) * self.orders_per_page

        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery_events),
            )
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(self.orders_per_page)
        )
        result = await self.session.execute(stmt)
        orders = result.scalars().all()

        return PaginatedUserOrders(orders, total_pages, page)

    async def get_order_details(self, order_id: int, user_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery_events),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _count_user_orders(self, user_id: int) -> int:
        stmt = select(func.count(Order.id)).where(Order.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()
