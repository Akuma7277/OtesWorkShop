from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shopim.db.models import (
    Admin,
    BalanceTransaction,
    BalanceTxType,
    Order,
    OrderItem,
    OrderStatus,
    StockMovement,
    StockMovementType,
)
from src.shopim.db.repositories.balance_repository import BalanceRepository


class OrderManagementService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def approve_order(self, order_id: int, admin: Admin) -> Order | None:
        order = await self.session.get(Order, order_id)
        if not order or order.status != OrderStatus.PENDING_ADMIN:
            return None

        order.status = OrderStatus.APPROVED
        order.approved_at = datetime.now(timezone.utc)
        order.delivery_deadline = order.approved_at + timedelta(hours=1)
        order.assigned_admin_id = admin.id

        await self.session.commit()
        return order

    async def reject_order(
        self, order_id: int, admin: Admin, reason: str
    ) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.status == OrderStatus.PENDING_ADMIN)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )

        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return None

        balance_repo = BalanceRepository(self.session)
        current_balance = await balance_repo.get_user_balance(order.user_id)
        balance_after = current_balance + order.total_amount

        refund_tx = BalanceTransaction(
            user_id=order.user_id,
            type=BalanceTxType.REFUND,
            amount=order.total_amount,
            balance_before=current_balance,
            balance_after=balance_after,
            reference_type="Order",
            reference_id=order.id,
            note=f"Buyurtma №{order.order_number} rad etilgani uchun qaytarildi",
        )
        self.session.add(refund_tx)

        for item in order.items:
            product = item.product
            stock_before = product.stock_grams
            product.stock_grams += item.grams

            stock_movement = StockMovement(
                product_id=item.product_id,
                type=StockMovementType.RETURN_IN,
                grams=item.grams,
                stock_before=stock_before,
                stock_after=product.stock_grams,
                reference_type="OrderItem",
                reference_id=item.id,
                reason=f"Buyurtma №{order.order_number} rad etildi",
            )
            self.session.add(stock_movement)

        order.status = OrderStatus.REJECTED
        order.rejection_reason = reason
        order.assigned_admin_id = admin.id

        await self.session.commit()
        return order
