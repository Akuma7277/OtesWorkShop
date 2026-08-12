from decimal import Decimal
from typing import Any

try:
    from slugify import slugify
except ImportError:
    import re

    def slugify(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[\s_-]+", "-", text)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import OrderItem, Product, StockMovement, StockMovementType
from src.shopim.db.repositories.product_repository import ProductRepository


class ProductManagementService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)

    async def create_product(
        self, product_data: dict[str, Any], admin_id: int
    ) -> Product:
        async with self.session.begin():
            # Generate a unique slug
            base_slug = slugify(product_data["name"])
            slug = base_slug
            counter = 1
            while await self.product_repo.get_by_slug(slug):
                slug = f"{base_slug}-{counter}"
                counter += 1

            category_id = product_data.get("category_id")
            if not category_id:
                from src.shopim.db.models import Category
                cat_stmt = select(Category).limit(1)
                cat_res = (await self.session.execute(cat_stmt)).scalar()
                if not cat_res:
                    cat_res = Category(name="Бишкек", is_active=True)
                    self.session.add(cat_res)
                    await self.session.flush()
                category_id = cat_res.id

            initial_stock = Decimal(product_data.get("initial_stock", "0"))
            cost_price = Decimal(product_data.get("cost_price", product_data.get("sale_price", "0")))

            new_product = Product(
                name=product_data["name"],
                slug=slug,
                category_id=category_id,
                description=product_data.get("description"),
                pickup_address=product_data.get("pickup_address"),
                image_file_id=product_data.get("image_file_id"),
                cost_price_per_gram=cost_price,
                sale_price_per_gram=Decimal(product_data["sale_price"]),
                stock_grams=initial_stock,
                low_stock_threshold_grams=Decimal(
                    product_data.get("low_stock_threshold", "10")
                ),
                created_by=admin_id,
                is_active=True,
            )
            self.session.add(new_product)
            await self.session.flush()

            if initial_stock > 0:
                stock_movement = StockMovement(
                    product_id=new_product.id,
                    type=StockMovementType.PURCHASE_IN,
                    grams=initial_stock,
                    stock_before=0,
                    stock_after=initial_stock,
                    reason="Boshlang'ich qoldiq",
                    created_by_admin_id=admin_id,
                )
                self.session.add(stock_movement)

            await self.session.flush()
            await self.session.refresh(new_product)
            return new_product

    async def can_delete_product(self, product_id: int) -> bool:
        """Checks if a product has any associated order items."""
        stmt = select(func.count(OrderItem.id)).where(OrderItem.product_id == product_id)
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count == 0

    async def delete_product(self, product_id: int) -> bool:
        """Deletes a product if it has no dependencies. Returns True on success."""
        if not await self.can_delete_product(product_id):
            return False

        async with self.session.begin():
            product = await self.product_repo.get(product_id)
            if product:
                await self.session.delete(product)
                await self.session.flush()
                return True
        return False

    async def update_product(
        self, product_id: int, update_data: dict[str, Any]
    ) -> Product | None:
        async with self.session.begin():
            product = await self.product_repo.get(product_id)
            if not product:
                return None

            for key, value in update_data.items():
                if hasattr(product, key):
                    # Special handling for slug if name changes
                    if key == "name" and value != product.name:
                        base_slug = slugify(value)
                        slug = base_slug
                        counter = 1
                        while True:
                            existing_product = await self.product_repo.get_by_slug(slug)
                            if not existing_product or existing_product.id == product.id:
                                break
                            slug = f"{base_slug}-{counter}"
                            counter += 1
                        product.slug = slug

                    # Convert to Decimal if needed
                    if key in [
                        "cost_price_per_gram",
                        "sale_price_per_gram",
                        "low_stock_threshold_grams",
                    ]:
                        value = Decimal(value)

                    setattr(product, key, value)

            await self.session.flush()
            await self.session.refresh(product)
            return product
