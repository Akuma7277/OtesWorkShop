import math
from decimal import Decimal
from typing import NamedTuple, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import BalanceTransaction
from src.shopim.db.repositories.balance_repository import BalanceRepository
from src.shopim.db.repositories.balance_transaction_repository import (
    BalanceTransactionRepository,
)


class BalanceHistory(NamedTuple):
    current_balance: Decimal
    transactions: Sequence[BalanceTransaction]
    total_pages: int
    current_page: int


class BalanceService:
    def __init__(self, session: AsyncSession, items_per_page: int = 10):
        self.session = session
        self.balance_repo = BalanceRepository(session)
        self.tx_repo = BalanceTransactionRepository(session)
        self.items_per_page = items_per_page

    async def get_balance_and_history(
        self, user_id: int, page: int = 1
    ) -> BalanceHistory:
        current_balance = await self.balance_repo.get_user_balance(user_id)

        total_tx = await self.tx_repo.count_for_user(user_id)
        if total_tx == 0:
            return BalanceHistory(current_balance, [], 0, page)

        total_pages = math.ceil(total_tx / self.items_per_page)
        offset = (page - 1) * self.items_per_page

        transactions = await self.tx_repo.get_paginated_for_user(
            user_id=user_id, offset=offset, limit=self.items_per_page
        )

        return BalanceHistory(current_balance, transactions, total_pages, page)