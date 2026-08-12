import math
from decimal import Decimal
from typing import NamedTuple, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Product, StockMovement, StockMovementType
from src.shopim.db.repositories.product_repository import ProductRepository
from src.shopim.db.repositories.stock_movement_repository import (
    StockMovementRepository,
)


class PaginatedProductsStock(NamedTuple):
    products: Sequence[Product]
    total_pages: int
    current_page: int


class PaginatedStockMovements(NamedTuple):
    movements: Sequence[StockMovement]
    total_pages: int
    current_page: int


class WarehouseService:
    def __init__(self, session: AsyncSession, items_per_page: int = 10):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.movement_repo = StockMovementRepository(session)
        self.items_per_page = items_per_page

    async def get_products_stock(self, page: int = 1) -> PaginatedProductsStock:
        total_products = await self.product_repo.count_all()
        if total_products == 0:
            return PaginatedProductsStock([], 0, page)

        total_pages = math.ceil(total_products / self.items_per_page)
        offset = (page - 1) * self.items_per_page

        products = await self.product_repo.get_all_paginated(
            offset=offset, limit=self.items_per_page
        )
        return PaginatedProductsStock(products, total_pages, page)

    async def get_stock_movements(self, page: int = 1) -> PaginatedStockMovements:
        total_movements = await self.movement_repo.count_movements()
        if total_movements == 0:
            return PaginatedStockMovements([], 0, page)

        total_pages = math.ceil(total_movements / self.items_per_page)
        offset = (page - 1) * self.items_per_page

        movements = await self.movement_repo.get_paginated_movements(
            offset=offset, limit=self.items_per_page
        )
        return PaginatedStockMovements(movements, total_pages, page)

    async def adjust_stock(
        self, product_id: int, grams: Decimal, reason: str, admin_id: int
    ) -> Product | None:
        """
        Adjusts product stock within a transaction.
        - Positive grams: ADJUSTMENT_IN
        - Negative grams: ADJUSTMENT_OUT
        """
        if grams == 0:
            return None

        async with self.session.begin():
            product = await self.product_repo.get_by_id_for_update(product_id)
            if not product:
                return None

            stock_before = product.stock_grams
            new_stock = stock_before + grams

            if new_stock < 0:
                return None  # Or raise an error

            product.stock_grams = new_stock

            movement_type = (
                StockMovementType.ADJUSTMENT_IN
                if grams > 0
                else StockMovementType.ADJUSTMENT_OUT
            )

            stock_movement = StockMovement(
                product_id=product.id,
                type=movement_type,
                grams=abs(grams),
                stock_before=stock_before,
                stock_after=new_stock,
                reason=reason,
                created_by_admin_id=admin_id,
            )
            self.session.add(stock_movement)
            self.session.add(product)

            await self.session.flush()
            return product