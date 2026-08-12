# ruff: noqa: D101, D102, D103, D104, D105, D107
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User
from src.shopim.db.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(self.model).where(
            self.model.telegram_id == telegram_id, self.model.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def user_exists(self, telegram_id: int) -> bool:
        stmt = select(self.model.id).where(self.model.telegram_id == telegram_id)
        result = await self.session.execute(select(stmt.exists()))
        return result.scalar()

    async def search_paginated(self, query: str, offset: int, limit: int):
        search_query = f"%{query}%"
        try:
            telegram_id_query = int(query)
        except ValueError:
            telegram_id_query = -1  # Impossible ID

        stmt = (
            select(self.model)
            .where(
                or_(
                    self.model.full_name.ilike(search_query),
                    self.model.username.ilike(search_query),
                    self.model.telegram_id == telegram_id_query,
                ),
                self.model.is_deleted == False,
            )
            .order_by(self.model.full_name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_search(self, query: str) -> int:
        search_query = f"%{query}%"
        try:
            telegram_id_query = int(query)
        except ValueError:
            telegram_id_query = -1

        stmt = select(func.count(self.model.id)).where(
            or_(
                self.model.full_name.ilike(search_query),
                self.model.username.ilike(search_query),
                self.model.telegram_id == telegram_id_query,
            ),
            self.model.is_deleted == False,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
