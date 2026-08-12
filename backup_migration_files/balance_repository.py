from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import BalanceTransaction


class BalanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_balance(self, user_id: int) -> Decimal:
        """Calculates the user's current balance by summing all transactions."""
        stmt = select(func.sum(BalanceTransaction.amount)).where(
            BalanceTransaction.user_id == user_id
        )
        result = await self.session.execute(stmt)
        balance = result.scalar_one_or_none()
        return balance if balance is not None else Decimal("0.00")