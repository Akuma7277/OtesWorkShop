# ruff: noqa: D101, D102, D103, D104, D105, D107
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.shopim.db.models import BalanceTxType, TopupStatus
from src.shopim.schemas.user import UserSchema


class TopupCreate(BaseModel):
    user_id: int
    amount: Decimal = Field(..., max_digits=18, decimal_places=2)
    payment_method: str
    receipt_file_id: str | None


class TopupSchema(BaseModel):
    id: int
    user: UserSchema
    amount: Decimal
    payment_method: str
    receipt_file_id: str | None
    status: TopupStatus
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceTransactionSchema(BaseModel):
    id: int
    user: UserSchema
    type: BalanceTxType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
