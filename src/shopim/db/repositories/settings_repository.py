from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import AppSettings


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_setting(self, key: str) -> AppSettings | None:
        return await self.session.get(AppSettings, key)

    async def set_setting(
        self, key: str, value: dict[str, Any], updated_by: int
    ) -> AppSettings:
        stmt = insert(AppSettings).values(key=key, value=value, updated_by=updated_by)
        stmt = stmt.on_conflict_do_update(
            index_elements=["key"],
            set_={
                "value": stmt.excluded.value,
                "updated_by": stmt.excluded.updated_by,
                "updated_at": "now()",
            },
        ).returning(AppSettings)

        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one()