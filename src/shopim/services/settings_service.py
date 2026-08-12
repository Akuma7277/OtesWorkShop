from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.settings_models import BotSettings
from src.shopim.db.repositories.settings_repository import SettingsRepository

BOT_SETTINGS_KEY = "bot_settings"


class SettingsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings_repo = SettingsRepository(session)

    async def get_bot_settings(self) -> BotSettings:
        """
        Retrieves bot settings from the database.
        If not found, returns default settings without saving them.
        """
        setting_db = await self.settings_repo.get_setting(BOT_SETTINGS_KEY)
        if setting_db and isinstance(setting_db.value, dict):
            return BotSettings.model_validate(setting_db.value)
        return BotSettings()

    async def update_bot_settings(
        self, update_data: dict[str, Any], admin_id: int
    ) -> BotSettings:
        """
        Updates bot settings, validates them, and saves to the database.
        """
        current_settings = await self.get_bot_settings()
        updated_settings_model = current_settings.model_copy(update=update_data)

        await self.settings_repo.set_setting(
            key=BOT_SETTINGS_KEY,
            value=updated_settings_model.model_dump(mode="json"),
            updated_by=admin_id,
        )
        return updated_settings_model