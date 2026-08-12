import math
from typing import NamedTuple, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Category, Product
from src.shopim.db.repositories.category_repository import CategoryRepository
from src.shopim.db.repositories.product_repository import ProductRepository


class PaginatedProducts(NamedTuple):
    products: Sequence[Product]
    total_pages: int
    current_page: int


class CatalogService:
    def __init__(self, session: AsyncSession, products_per_page: int = 5):
        self.session = session
        self.category_repo = CategoryRepository(session)
        self.product_repo = ProductRepository(session)
        self.products_per_page = products_per_page

    async def get_all_active_categories(self) -> Sequence[Category]:
        return await self.category_repo.get_all_active()

    async def get_paginated_products_by_category(
        self, category_id: int, page: int = 1
    ) -> PaginatedProducts:
        total_products = await self.product_repo.count_by_category(category_id)
        if total_products == 0:
            return PaginatedProducts([], 0, page)

        total_pages = math.ceil(total_products / self.products_per_page)
        offset = (page - 1) * self.products_per_page

        products = await self.product_repo.get_paginated_by_category(
            category_id=category_id, offset=offset, limit=self.products_per_page
        )

        return PaginatedProducts(products, total_pages, page)

    async def get_product_by_id(self, product_id: int) -> Product | None:
        return await self.product_repo.get_by_id(product_id)

    async def search_products(self, query: str, page: int = 1) -> PaginatedProducts:
        total_products = await self.product_repo.count_search(query)
        if total_products == 0:
            return PaginatedProducts([], 0, page)

        total_pages = math.ceil(total_products / self.products_per_page)
        offset = (page - 1) * self.products_per_page

        products = await self.product_repo.search_paginated(
            query=query, offset=offset, limit=self.products_per_page
        )

        return PaginatedProducts(products, total_pages, page)