from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.shopim.db.repositories.user_repository import UserRepository

class RegistrationService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.session = session

    async def start_registration(self, telegram_id: int):
        # In a real scenario, we might create a registration session
        # or pre-populate some data. For now, we just check existence.
        return await self.user_repo.user_exists(telegram_id)

    async def create_pending_user(
        self,
        telegram_id: int,
        full_name: str,
        phone: str,
        address: str,
        age: int,
        language_code: str,
        username: Optional[str] = None,
    ):
        """
        Creates a new user with PENDING status and commits the transaction.
        """
        user = await self.user_repo.create( # type: ignore
            telegram_id=telegram_id,
            full_name=full_name,
            phone=phone,
            address=address,
            age=age,
            username=username,
            language_code=language_code,
        )
        # The service is responsible for committing the transaction
        await self.session.commit()
        # The user object is now "expired", we should refresh it to get DB defaults
        await self.session.refresh(user)
        return user
