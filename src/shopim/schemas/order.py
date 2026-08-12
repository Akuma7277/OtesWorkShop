# ruff: noqa: D101, D102, D103, D104, D105, D107
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.shopim.db.models import OrderStatus
from src.shopim.schemas.product import ProductSchema
from src.shopim.schemas.user import UserSchema


class OrderItemCreate(BaseModel):
    product_id: int
    grams: Decimal = Field(..., max_digits=18, decimal_places=3)


class OrderItemSchema(BaseModel):
    id: int
    product: ProductSchema
    product_name_snapshot: str
    grams: Decimal
    unit_price_per_gram: Decimal
    cost_price_per_gram_snapshot: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    user_id: int
    delivery_address: str
    items: list[OrderItemCreate]


class OrderSchema(BaseModel):
    id: int
    order_number: str
    user: UserSchema
    status: OrderStatus
    total_amount: Decimal
    delivery_address: str
    delivery_deadline: datetime | None
    items: list[OrderItemSchema]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
