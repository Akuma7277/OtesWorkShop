# ruff: noqa: D101, D102, D103, D104, D105, D107
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str


class CategorySchema(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    category_id: int | None
    description: str | None
    cost_price_per_gram: Decimal = Field(..., max_digits=18, decimal_places=2)
    sale_price_per_gram: Decimal = Field(..., max_digits=18, decimal_places=2)
    low_stock_threshold_grams: Decimal = Field(..., max_digits=18, decimal_places=3)
    stock_grams: Decimal = Field(..., max_digits=18, decimal_places=3)
    is_active: bool = True


class ProductSchema(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image_file_id: str | None
    image_url: str | None
    cost_price_per_gram: Decimal
    sale_price_per_gram: Decimal
    stock_grams: Decimal
    low_stock_threshold_grams: Decimal
    is_active: bool
    category: CategorySchema | None

    class Config:
        from_attributes = True
        
