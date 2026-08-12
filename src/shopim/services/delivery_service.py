from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, DeliveryEvent, Order, OrderStatus
from src.shopim.db.repositories.order_repository import OrderRepository


class DeliveryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)

    async def update_delivery_status(
        self, order_id: int, new_status: OrderStatus, admin: Admin
    ) -> Order | None:
        """Updates the order status and creates a delivery event in a transaction."""
        async with self.session.begin():
            order = await self.order_repo.get(order_id)
            if not order:
                return None

            # Basic state transition validation
            valid_transitions = {
                OrderStatus.APPROVED: [OrderStatus.PACKING],
                OrderStatus.PACKING: [OrderStatus.OUT_FOR_DELIVERY],
                OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED],
            }

            if new_status not in valid_transitions.get(order.status, []):
                # Invalid transition, do nothing
                return None

            order.status = new_status

            delivery_event = DeliveryEvent(
                order_id=order.id,
                status=new_status.name,
                created_by_admin_id=admin.id,
            )
            self.session.add(delivery_event)

            if new_status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.now(timezone.utc)

            await self.session.flush()
            await self.session.refresh(order)
            return order