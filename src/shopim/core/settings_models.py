from decimal import Decimal

from pydantic import BaseModel, Field


class BotSettings(BaseModel):
    min_user_age: int = Field(default=13, description="Minimal yosh")
    max_user_age: int = Field(default=120, description="Maksimal yosh")
    min_topup_amount: Decimal = Field(default=Decimal("1000.00"), description="Minimal to'lov summasi")
    delivery_sla_hours: int = Field(default=1, description="Yetkazib berish SLA (soat)")
    low_stock_notify_interval_hours: int = Field(default=24, description="Kam qoldiq haqida qayta xabar intervali (soat)")
    operator_contact: str = Field(default="@operator", description="Operator kontakti")
    currency_symbol: str = Field(default="so'm", description="Valyuta belgisi")