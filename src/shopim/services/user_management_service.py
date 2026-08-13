import math
from decimal import Decimal
from typing import NamedTuple, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.shopim.db.models import (
    Admin,
    BalanceTransaction,
    BalanceTxType,
    User,
    UserStatus,
)
from src.shopim.db.repositories.user_repository import UserRepository

class PaginatedUsers(NamedTuple):
    users: Sequence[User]
    total_pages: int
    current_page: int

class UserManagementService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def approve_user(self, user_id: int, admin: Admin) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user or user.status != UserStatus.PENDING:
            return None
        
        user.status = UserStatus.APPROVED
        self.session.add(user)
        # TODO: Create audit log entry
        await self.session.commit()
        return user

    async def reject_user(self, user_id: int, admin: Admin, reason: str) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user or user.status != UserStatus.PENDING:
            return None
            
        user.status = UserStatus.REJECTED
        user.rejection_reason = reason
        self.session.add(user)
        # TODO: Create audit log entry
        await self.session.commit()
        return user

    async def search_users(
        self, query: str, page: int = 1, items_per_page: int = 5
    ) -> PaginatedUsers:
        total_users = await self.user_repo.count_search(query)
        if total_users == 0:
            return PaginatedUsers([], 0, page)

        total_pages = math.ceil(total_users / items_per_page)
        offset = (page - 1) * items_per_page

        users = await self.user_repo.search_paginated(
            query=query, offset=offset, limit=items_per_page
        )
        return PaginatedUsers(users, total_pages, page)

    async def toggle_user_block(self, user_id: int, admin: Admin) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user or user.status not in [UserStatus.APPROVED, UserStatus.BLOCKED]:
            return None

        if user.status == UserStatus.BLOCKED:
            user.status = UserStatus.APPROVED
        else:
            user.status = UserStatus.BLOCKED

        # TODO: Create audit log entry
        await self.session.commit()
        return user

    async def adjust_user_balance(
        self, user_id: int, amount: Decimal, reason: str, admin: Admin
    ) -> Optional[BalanceTransaction]:
        from src.shopim.db.repositories.balance_repository import BalanceRepository

        user = await self.user_repo.get(user_id)
        if not user:
            return None

        balance_repo = BalanceRepository(self.session)
        balance_before = await balance_repo.get_user_balance(user_id)
        balance_after = balance_before + amount

        tx_type = (
            BalanceTxType.MANUAL_CREDIT
            if amount > 0
            else BalanceTxType.MANUAL_DEBIT
        )

        balance_tx = BalanceTransaction(
            user_id=user_id,
            type=tx_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            note=reason,
            created_by_admin_id=admin.id,
        )
        self.session.add(balance_tx)
        await self.session.commit()
        await self.session.refresh(balance_tx)
        return balance_tx
