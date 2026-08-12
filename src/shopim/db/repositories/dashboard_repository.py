from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
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
        return result.scalar_one() or Decimal("0.00")

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
        return result.scalar_one() or Decimal("0.00")

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