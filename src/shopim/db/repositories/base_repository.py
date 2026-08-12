# ruff: noqa: D101, D102, D103, D104, D105, D107
from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Base

Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    def __init__(self, session: AsyncSession, model: Type[Model]):
        self.session = session
        self.model = model

    async def get(self, pk: int) -> Model | None:
        return await self.session.get(self.model, pk)

    async def get_all(self) -> list[Model]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Model:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, pk: int, **kwargs) -> Model | None:
        instance = await self.get(pk)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance

    async def delete(self, pk: int) -> bool:
        instance = await self.get(pk)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False
