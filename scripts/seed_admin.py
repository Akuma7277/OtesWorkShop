import asyncio
import argparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.session import create_async_engine, create_session_pool
from src.shopim.db.models import Admin, AdminRole
from src.shopim.core.config import get_settings

async def seed_super_admin(telegram_id: int, full_name: str):
    """
    Creates or updates a user to be a SUPER_ADMIN.
    """
    print("Starting admin seed script...")
    settings = get_settings()
    engine = create_async_engine(settings.db_url)
    
    # Create tables if they don't exist (especially for SQLite)
    from src.shopim.db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        session: AsyncSession
        stmt = select(Admin).where(Admin.telegram_id == telegram_id)
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()

        if admin:
            print(f"Admin with Telegram ID {telegram_id} already exists. Updating role to SUPER_ADMIN.")
            admin.role = AdminRole.SUPER_ADMIN
            admin.is_active = True
            admin.full_name = full_name
        else:
            print(f"Creating new SUPER_ADMIN with Telegram ID {telegram_id}.")
            admin = Admin(
                telegram_id=telegram_id,
                full_name=full_name,
                role=AdminRole.SUPER_ADMIN,
                is_active=True
            )
        
        session.add(admin)
        await session.commit()
        print("Successfully seeded super admin.")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed a SUPER_ADMIN for the Shopim Bot.")
    parser.add_argument("telegram_id", type=int, help="The Telegram ID of the user to make a super admin.")
    parser.add_argument("full_name", type=str, help="The full name of the super admin.")
    args = parser.parse_args()
    
    # It's better to load .env file explicitly here if run as a standalone script
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(seed_super_admin(telegram_id=args.telegram_id, full_name=args.full_name))
