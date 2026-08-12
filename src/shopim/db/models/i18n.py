from typing import Any, Dict

from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import I18nMiddleware

from src.shopim.db.models import Admin, User


I18N_DOMAIN = "bot"
LOCALES_DIR = "locales"

i18n = I18n(
    path=LOCALES_DIR,
    default_locale="uz",
    domain=I18N_DOMAIN,
)


class LanguageMiddleware(I18nMiddleware):
    def __init__(self) -> None:
        super().__init__(i18n=i18n)

    async def get_locale(
        self,
        event: Any,
        data: Dict[str, Any],
    ) -> str:
        user: User | Admin | None = data.get("user") or data.get("admin")

        if user and getattr(user, "language_code", None):
            lang = str(user.language_code).strip().lower()
            if lang in ("uz", "ru"):
                return lang

        state = data.get("state")
        if state:
            state_data = await state.get_data()
            if "language_code" in state_data:
                lang = str(state_data["language_code"]).strip().lower()
                if lang in ("uz", "ru"):
                    return lang

        from_user = data.get("event_from_user") or getattr(event, "from_user", None)
        if from_user and getattr(from_user, "language_code", None):
            tg_lang = str(from_user.language_code).strip().lower()
            if tg_lang.startswith("ru"):
                return "ru"
            elif tg_lang.startswith("uz"):
                return "uz"

        return self.i18n.default_locale or "uz"
