import math
from typing import NamedTuple, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Order
from src.shopim.db.repositories.order_repository import OrderRepository


class PaginatedOrders(NamedTuple):
    orders: Sequence[Order]
    total_pages: int
    current_page: int


class OrderHistoryService:
    def __init__(self, session: AsyncSession, orders_per_page: int = 5):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.orders_per_page = orders_per_page

    async def get_user_orders(self, user_id: int, page: int = 1) -> PaginatedOrders:
        total_orders = await self.order_repo.count_for_user(user_id)
        if total_orders == 0:
            return PaginatedOrders([], 0, page)

        total_pages = math.ceil(total_orders / self.orders_per_page)
        offset = (page - 1) * self.orders_per_page

        orders = await self.order_repo.get_paginated_for_user(
            user_id=user_id, offset=offset, limit=self.orders_per_page
        )

        return PaginatedOrders(orders, total_pages, page)

    async def get_order_details(self, order_id: int, user_id: int) -> Order | None:
        return await self.order_repo.get_by_id_with_items(order_id, user_id)