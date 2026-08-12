from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import BalanceTransaction


class BalanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_balance(self, user_id: int) -> Decimal:
        """Calculates the current balance for a user by summing all transactions."""
        stmt = select(func.coalesce(func.sum(BalanceTransaction.amount), 0)).where(
            BalanceTransaction.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar_one()))
