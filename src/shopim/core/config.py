import os
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Bot
    bot_token: str = Field(default="", validation_alias="BOT_TOKEN")
    super_admin_ids: str = Field(default="", validation_alias="SUPER_ADMIN_IDS")

    # Database
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="shopim", validation_alias="POSTGRES_DB")
    database_url: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")

    # Redis
    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(default=0, validation_alias="REDIS_DB")
    redis_url: Optional[str] = Field(default=None, validation_alias="REDIS_URL")

    # App
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    currency_symbol: str = Field(default="so'm", validation_alias="CURRENCY_SYMBOL")

    # Business Logic
    min_user_age: int = Field(default=16, validation_alias="MIN_USER_AGE")
    max_user_age: int = Field(default=100, validation_alias="MAX_USER_AGE")
    min_topup_amount: float = Field(default=10000.0, validation_alias="MIN_TOPUP_AMOUNT")
    delivery_sla_minutes: int = Field(default=60, validation_alias="DELIVERY_SLA_MINUTES")
    low_stock_notify_interval_hours: int = Field(default=24, validation_alias="LOW_STOCK_NOTIFY_INTERVAL_HOURS")
    operator_contact: str = Field(default="@support", validation_alias="OPERATOR_CONTACT")
    mini_app_url: str = Field(default="", validation_alias="MINI_APP_URL")

    @property
    def get_mini_app_url(self) -> str:
        """
        Automatically detects the Mini App URL.
        Priority:
          1. Explicitly set MINI_APP_URL env variable
          2. RAILWAY_PUBLIC_DOMAIN (set automatically by Railway)
          3. RAILWAY_STATIC_URL
          4. Empty string (Mini App button will be hidden)
        """
        if self.mini_app_url:
            url = self.mini_app_url
            return url if url.startswith("http") else f"https://{url}"

        # Railway injects this automatically
        railway_domain = (
            os.getenv("RAILWAY_PUBLIC_DOMAIN")
            or os.getenv("RAILWAY_STATIC_URL")
        )
        if railway_domain:
            domain = railway_domain.removeprefix("https://").removeprefix("http://")
            return f"https://{domain}"

        # Fallback to the production domain so bot still works when run locally
        return "https://otesworkshop-production.up.railway.app"



    @property
    def db_url(self) -> str:
        # Check explicit DATABASE_URL or Railway environment variables
        url = (
            self.database_url
            or os.getenv("DATABASE_URL")
            or os.getenv("DATABASE_PRIVATE_URL")
            or os.getenv("DATABASE_PUBLIC_URL")
            or os.getenv("POSTGRES_URL")
            or os.getenv("POSTGRESQL_URL")
            or os.getenv("PGURL")
        )
        if url:
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        # Check explicit PGHOST / POSTGRES_HOST
        host = os.getenv("PGHOST") or os.getenv("POSTGRES_HOST")
        if host and host not in ("localhost", "127.0.0.1", "db"):
            port = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or self.postgres_port
            user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or self.postgres_user
            password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or self.postgres_password
            db = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or self.postgres_db
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

        # Automatic fallback to local SQLite database if no remote PostgreSQL is configured
        os.makedirs("./data", exist_ok=True)
        return "sqlite+aiosqlite:///./data/shopim.db"

    @property
    def get_redis_url(self) -> Optional[str]:
        return (
            self.redis_url
            or os.getenv("REDIS_URL")
            or os.getenv("REDIS_PRIVATE_URL")
            or os.getenv("REDIS_PUBLIC_URL")
        )

    @property
    def super_admins_list(self) -> list[int]:
        if not self.super_admin_ids:
            return []
        res = []
        for admin_id in self.super_admin_ids.split(','):
            cleaned = admin_id.strip()
            if cleaned.isdigit() or (cleaned.startswith('-') and cleaned[1:].isdigit()):
                res.append(int(cleaned))
        return res

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
