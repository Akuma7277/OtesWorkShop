import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import NamedTuple, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, BalanceTransaction, BalanceTxType, Topup, TopupStatus
from src.shopim.db.repositories.balance_repository import BalanceRepository
from src.shopim.db.repositories.topup_repository import TopupRepository


class PaginatedTopups(NamedTuple):
    topups: Sequence[Topup]
    total_pages: int
    current_page: int


class TopupManagementService:
    def __init__(self, session: AsyncSession, items_per_page: int = 5):
        self.session = session
        self.topup_repo = TopupRepository(session)
        self.items_per_page = items_per_page

    async def get_pending_topups(self, page: int = 1) -> PaginatedTopups:
        total_items = await self.topup_repo.count_pending()
        if total_items == 0:
            return PaginatedTopups([], 0, page)

        total_pages = math.ceil(total_items / self.items_per_page)
        offset = (page - 1) * self.items_per_page

        topups = await self.topup_repo.get_paginated_pending(
            offset=offset, limit=self.items_per_page
        )
        return PaginatedTopups(topups, total_pages, page)

    async def approve_topup(self, topup_id: int, admin: Admin) -> Topup | None:
        async with self.session.begin():
            topup = await self.topup_repo.get(topup_id)
            if not topup or topup.status != TopupStatus.PENDING:
                return None

            balance_repo = BalanceRepository(self.session)
            current_balance = await balance_repo.get_user_balance(topup.user_id)
            amount = Decimal(str(topup.amount))
            balance_after = current_balance + amount

            balance_tx = BalanceTransaction(
                user_id=topup.user_id,
                type=BalanceTxType.TOPUP,
                amount=amount,
                balance_before=current_balance,
                balance_after=balance_after,
                reference_type="Topup",
                reference_id=topup.id,
                created_by_admin_id=admin.id,
            )
            self.session.add(balance_tx)

            topup.status = TopupStatus.APPROVED
            topup.admin_id = admin.id
            topup.reviewed_at = datetime.now(timezone.utc)

            await self.session.flush()
            await self.session.refresh(topup)
            return topup

    async def reject_topup(self, topup_id: int, admin: Admin, reason: str) -> Topup | None:
        topup = await self.topup_repo.get(topup_id)
        if not topup or topup.status != TopupStatus.PENDING:
            return None

        topup.status = TopupStatus.REJECTED
        topup.admin_id = admin.id
        topup.reviewed_at = datetime.now(timezone.utc)
        topup.admin_note = reason

        await self.session.commit()
        return topup
