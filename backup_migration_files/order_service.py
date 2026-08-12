from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import (
    BalanceTransaction,
    BalanceTxType,
    Order,
    OrderItem,
    OrderStatus,
    StockMovement,
    StockMovementType,
    User,
)
from src.shopim.db.repositories.balance_repository import BalanceRepository
from src.shopim.db.repositories.product_repository import ProductRepository
from src.shopim.utils.order_number import generate_order_number


class OrderCreationError(Exception):
    """Custom exception for order creation failures."""

    pass


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.balance_repo = BalanceRepository(session)

    async def create_order(
        self,
        user: User,
        product_id: int,
        grams: Decimal,
        total_price: Decimal,
    ) -> Order:
        """
        Creates a new order within a single database transaction.
        Raises OrderCreationError on failure, which causes a rollback.
        """
        async with self.session.begin():
            # 1. Lock product for update and re-check stock
            product = await self.product_repo.get_by_id_for_update(product_id)

            if not product or not product.is_active:
                raise OrderCreationError("Mahsulot topilmadi yoki faol emas.")

            if product.stock_grams < grams:
                raise OrderCreationError(
                    f"Afsuski, omborda faqat {product.stock_grams} gramm qolgan."
                )

            # 2. Re-check user balance
            current_balance = await self.balance_repo.get_user_balance(user.id)
            if current_balance < total_price:
                raise OrderCreationError("Balansingizda mablag' yetarli emas.")

            # 3. Create Order
            new_order = Order(
                order_number=generate_order_number(),
                user_id=user.id,
                status=OrderStatus.PENDING_ADMIN,
                total_amount=total_price,
                delivery_address=user.address,
            )
            self.session.add(new_order)
            await self.session.flush()

            # 4. Create Order Item
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                grams=grams,
                unit_price_per_gram=product.sale_price_per_gram,
                cost_price_per_gram_snapshot=product.cost_price_per_gram,
                subtotal=total_price,
            )
            self.session.add(order_item)
            await self.session.flush()

            # 5. Create Balance Transaction (Debit)
            balance_after = current_balance - total_price
            balance_tx = BalanceTransaction(
                user_id=user.id,
                type=BalanceTxType.PURCHASE,
                amount=-total_price,
                balance_before=current_balance,
                balance_after=balance_after,
                reference_type="Order",
                reference_id=new_order.id,
            )
            self.session.add(balance_tx)

            # 6. Update Product Stock and create Stock Movement
            stock_before = product.stock_grams
            product.stock_grams -= grams
            stock_movement = StockMovement(
                product_id=product.id,
                type=StockMovementType.SALE_OUT,
                grams=grams,
                stock_before=stock_before,
                stock_after=product.stock_grams,
                reference_type="OrderItem",
                reference_id=order_item.id,
            )
            self.session.add(product)
            self.session.add(stock_movement)

            return new_order