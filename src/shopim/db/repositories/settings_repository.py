from datetime import datetime, timezone
from typing import Any

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
        now = datetime.now(timezone.utc)
        setting = await self.session.get(AppSettings, key)
        if setting:
            setting.value = value
            setting.updated_by = updated_by
            setting.updated_at = now
        else:
            setting = AppSettings(
                key=key,
                value=value,
                updated_by=updated_by,
                created_at=now,
                updated_at=now,
            )
        await self.session.flush()
        await self.session.commit()
        return setting