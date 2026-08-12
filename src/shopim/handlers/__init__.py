from aiogram import Dispatcher

from src.shopim.handlers.user.registration import router as user_registration_router
from src.shopim.handlers.miniapp import router as miniapp_router


def setup_routers(dp: Dispatcher):
    """Includes only Mini App related routers in the dispatcher.
    All old legacy text command handlers are removed.
    """
    dp.include_router(user_registration_router)
    dp.include_router(miniapp_router)
