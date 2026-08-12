from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.shopim.db.models import Admin

class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active_admins(self) -> list[Admin]:
        stmt = select(Admin).where(Admin.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
