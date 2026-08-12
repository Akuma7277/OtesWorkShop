from datetime import datetime
from decimal import Decimal
from typing import Any, List, Sequence, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import (
    Order,
    OrderItem,
    OrderStatus,
    Product,
    Topup,
    TopupStatus,
    User,
    UserStatus,
)


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_orders_today_count(self, today_start: datetime) -> int:
        stmt = select(func.count(Order.id)).where(Order.created_at >= today_start)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_revenue_today(self, today_start: datetime) -> Decimal:
        stmt = select(func.sum(Order.total_amount)).where(
            Order.created_at >= today_start,
            Order.status.in_(
                [
                    OrderStatus.APPROVED,
                    OrderStatus.PACKING,
                    OrderStatus.OUT_FOR_DELIVERY,
                    OrderStatus.DELIVERED,
                ]
            ),
        )
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        return Decimal(str(val)) if val is not None else Decimal("0.00")

    async def get_profit_today(self, today_start: datetime) -> Decimal:
        stmt = select(
            func.sum(
                (OrderItem.unit_price_per_gram - OrderItem.cost_price_per_gram_snapshot)
                * OrderItem.grams
            )
        ).join(Order, Order.id == OrderItem.order_id).where(
            Order.created_at >= today_start,
            Order.status.in_(
                [
                    OrderStatus.APPROVED,
                    OrderStatus.PACKING,
                    OrderStatus.OUT_FOR_DELIVERY,
                    OrderStatus.DELIVERED,
                ]
            ),
        )
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        return Decimal(str(val)) if val is not None else Decimal("0.00")

    async def get_total_revenue(self) -> Decimal:
        stmt = select(func.sum(Order.total_amount)).where(
            Order.status.in_(
                [
                    OrderStatus.APPROVED,
                    OrderStatus.PACKING,
                    OrderStatus.OUT_FOR_DELIVERY,
                    OrderStatus.DELIVERED,
                ]
            )
        )
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        return Decimal(str(val)) if val is not None else Decimal("0.00")

    async def get_total_grams_sold(self) -> Decimal:
        stmt = select(func.sum(OrderItem.grams)).join(Order, Order.id == OrderItem.order_id).where(
            Order.status.in_(
                [
                    OrderStatus.APPROVED,
                    OrderStatus.PACKING,
                    OrderStatus.OUT_FOR_DELIVERY,
                    OrderStatus.DELIVERED,
                ]
            )
        )
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        return Decimal(str(val)) if val is not None else Decimal("0.00")

    async def get_total_orders_count(self) -> int:
        stmt = select(func.count(Order.id))
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_top_buyers(self, limit: int = 10) -> List[Tuple[User, int, Decimal, Decimal]]:
        """
        Returns list of (User, orders_count, total_spent_usd, total_grams_bought)
        """
        stmt = (
            select(
                User,
                func.count(Order.id).label("orders_count"),
                func.coalesce(func.sum(Order.total_amount), 0).label("total_spent"),
                func.coalesce(func.sum(OrderItem.grams), 0).label("total_grams"),
            )
            .join(Order, Order.user_id == User.id)
            .outerjoin(OrderItem, OrderItem.order_id == Order.id)
            .where(
                Order.status.in_(
                    [
                        OrderStatus.APPROVED,
                        OrderStatus.PACKING,
                        OrderStatus.OUT_FOR_DELIVERY,
                        OrderStatus.DELIVERED,
                    ]
                )
            )
            .group_by(User.id)
            .order_by(desc("total_spent"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = []
        for row in result.all():
            u, count, spent, grams = row
            items.append((u, count, Decimal(str(spent)), Decimal(str(grams))))
        return items

    async def get_pending_registrations_count(self) -> int:
        stmt = select(func.count(User.id)).where(User.status == UserStatus.PENDING)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_pending_topups_count(self) -> int:
        stmt = select(func.count(Topup.id)).where(Topup.status == TopupStatus.PENDING)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_pending_orders_count(self) -> int:
        stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING_ADMIN)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_active_users_count(self) -> int:
        stmt = select(func.count(User.id)).where(User.status == UserStatus.APPROVED)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_low_stock_products_count(self) -> int:
        stmt = select(func.count(Product.id)).where(
            Product.stock_grams <= Product.low_stock_threshold_grams,
            Product.is_active == True,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0