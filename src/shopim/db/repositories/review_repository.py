from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.shopim.db.models import Review, ReviewStatus
from src.shopim.db.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Review)

    async def create_review(self, user_id: int, text: str, rating: int = 5) -> Review:
        review = Review(
            user_id=user_id,
            text=text,
            rating=rating,
            status=ReviewStatus.PENDING,
        )
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def get_by_id_with_user(self, review_id: int) -> Review | None:
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.id == review_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_reviews(self) -> Sequence[Review]:
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.status == ReviewStatus.PENDING)
            .order_by(Review.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_approved_reviews(self, limit: int = 20) -> Sequence[Review]:
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.status == ReviewStatus.APPROVED)
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_review_status(
        self, review_id: int, status: ReviewStatus, channel_message_id: int | None = None
    ) -> Review | None:
        review = await self.get_by_id_with_user(review_id)
        if not review:
            return None
        review.status = status
        if channel_message_id is not None:
            review.channel_message_id = channel_message_id
        await self.session.commit()
        await self.session.refresh(review)
        return review
