from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Topup


class TopupService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pending_topup(
        self,
        user_id: int,
        amount: Decimal,
        receipt_file_id: str,
        payment_method: str = "manual",
    ) -> Topup:
        """Creates a new topup request with PENDING status."""
        topup = Topup(
            user_id=user_id,
            amount=amount,
            receipt_file_id=receipt_file_id,
            payment_method=payment_method,
        )
        self.session.add(topup)
        await self.session.flush()
        await self.session.refresh(topup)
        return topup
