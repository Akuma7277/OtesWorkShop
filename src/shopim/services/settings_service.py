from decimal import Decimal
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
            val_dict = dict(setting_db.value)
            try:
                min_topup = Decimal(str(val_dict.get("min_topup_amount", "1000.00")))
                if min_topup >= Decimal("1000.00"):
                    val_dict["min_topup_amount"] = 5.0
            except Exception:
                pass
            return BotSettings.model_validate(val_dict)
        return BotSettings()

    async def update_bot_settings(
        self, update_data: dict[str, Any], admin_id: int
    ) -> BotSettings:
        """
        Updates bot settings, validates them, and saves to the database.
        """
        current_settings = await self.get_bot_settings()
        current_dict = current_settings.model_dump()

        for key, val in update_data.items():
            if key in BotSettings.model_fields:
                field_type = BotSettings.model_fields[key].annotation
                if field_type == int:
                    val = int(val)
                elif field_type == Decimal:
                    val = Decimal(str(val))
                current_dict[key] = str(val) if isinstance(val, str) else val

        updated_settings_model = BotSettings.model_validate(current_dict)

        await self.settings_repo.set_setting(
            key=BOT_SETTINGS_KEY,
            value=updated_settings_model.model_dump(mode="json"),
            updated_by=admin_id,
        )
        return updated_settings_model