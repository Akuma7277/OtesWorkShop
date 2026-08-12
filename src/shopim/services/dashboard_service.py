from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User
from src.shopim.db.repositories.dashboard_repository import DashboardRepository


@dataclass
class DashboardStats:
    orders_today_count: int = 0
    revenue_today: Decimal = Decimal("0.00")
    profit_today: Decimal = Decimal("0.00")
    total_orders_count: int = 0
    total_revenue: Decimal = Decimal("0.00")
    total_grams_sold: Decimal = Decimal("0.00")
    pending_registrations_count: int = 0
    pending_topups_count: int = 0
    pending_orders_count: int = 0
    active_users_count: int = 0
    low_stock_products_count: int = 0
    top_buyers: List[Tuple[User, int, Decimal, Decimal]] = field(default_factory=list)


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.dashboard_repo = DashboardRepository(session)

    async def get_stats(self) -> DashboardStats:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        stats = DashboardStats()
        stats.orders_today_count = await self.dashboard_repo.get_orders_today_count(
            today_start
        )
        stats.revenue_today = await self.dashboard_repo.get_revenue_today(today_start)
        stats.profit_today = await self.dashboard_repo.get_profit_today(today_start)
        stats.total_orders_count = await self.dashboard_repo.get_total_orders_count()
        stats.total_revenue = await self.dashboard_repo.get_total_revenue()
        stats.total_grams_sold = await self.dashboard_repo.get_total_grams_sold()
        stats.pending_registrations_count = (
            await self.dashboard_repo.get_pending_registrations_count()
        )
        stats.pending_topups_count = await self.dashboard_repo.get_pending_topups_count()
        stats.pending_orders_count = await self.dashboard_repo.get_pending_orders_count()
        stats.active_users_count = await self.dashboard_repo.get_active_users_count()
        stats.low_stock_products_count = (
            await self.dashboard_repo.get_low_stock_products_count()
        )
        stats.top_buyers = await self.dashboard_repo.get_top_buyers(limit=10)

        return stats