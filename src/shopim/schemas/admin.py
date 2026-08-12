# ruff: noqa: D101, D102, D103, D104, D105, D107
from pydantic import BaseModel

from src.shopim.db.models import AdminRole


class AdminCreate(BaseModel):
    telegram_id: int
    full_name: str
    role: AdminRole


class AdminSchema(BaseModel):
    id: int
    telegram_id: int
    full_name: str
    role: AdminRole
    is_active: bool

    class Config:
        from_attributes = True
