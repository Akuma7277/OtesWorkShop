# ruff: noqa: D101, D102, D103, D104, D105, D107
from pydantic import BaseModel, constr


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None
    full_name: constr(min_length=1)
    phone: constr(min_length=5) | None
    address: constr(min_length=1)
    age: int


class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    full_name: str
    phone: str | None
    address: str
    age: int

    class Config:
        from_attributes = True
