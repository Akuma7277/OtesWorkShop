from decimal import Decimal

from pydantic import BaseModel, Field


class BotSettings(BaseModel):
    min_user_age: int = Field(default=13, description="Minimal yosh")
    max_user_age: int = Field(default=120, description="Maksimal yosh")
    min_topup_amount: Decimal = Field(default=Decimal("5.00"), description="Minimal to'lov summasi")
    delivery_sla_hours: int = Field(default=1, description="Yetkazib berish SLA (soat)")
    low_stock_notify_interval_hours: int = Field(default=24, description="Kam qoldiq haqida qayta xabar intervali (soat)")
    operator_contact: str = Field(default="tg://user?id=8287529253", description="Operator kontakti")
    currency_symbol: str = Field(default="USD", description="Valyuta belgisi")
    reviews_channel_id: str = Field(default="", description="Otzivlar kanali ID/Username (@channel)")
    ltc_wallet_address: str = Field(default="ltc1q05lr7y93kfs0afj5x2hadnsdtzd6cm9werlv6x", description="LTC hamyon manzili")
    usdt_wallet_address: str = Field(default="TR7NHqjeKQGJmG4q89uU8865B6149D09W1", description="USDT TRC20 hamyon manzili")
    job_info_text: str = Field(default="💼 Работа! ПЛАТИМ ДОХУЯ!\n\nПодробности у оператора.", description="Ish haqida ma'lumot")