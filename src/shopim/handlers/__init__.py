from aiogram import Dispatcher

from src.shopim.handlers.admin.dashboard import router as admin_dashboard_router
from src.shopim.handlers.admin.delivery_management import (
    router as admin_delivery_management_router,
)
from src.shopim.handlers.admin.main_menu import router as admin_main_menu_router
from src.shopim.handlers.admin.order_management import (
    router as admin_order_management_router,
)
from src.shopim.handlers.admin.product_editing import (
    router as admin_product_editing_router,
)
from src.shopim.handlers.admin.product_management import (
    router as admin_product_management_router,
)
from src.shopim.handlers.admin.review_moderation import (
    router as admin_review_moderation_router,
)
from src.shopim.handlers.admin.settings_management import (
    router as admin_settings_management_router,
)
from src.shopim.handlers.admin.topup_management import (
    router as admin_topup_management_router,
)
from src.shopim.handlers.admin.user_management import (
    router as admin_user_management_router,
)
from src.shopim.handlers.admin.warehouse import router as admin_warehouse_router

from src.shopim.handlers.user.balance import router as user_balance_router
from src.shopim.handlers.user.order_history import (
    router as user_order_history_router,
)
from src.shopim.handlers.user.profile import router as user_profile_router
from src.shopim.handlers.user.registration import router as user_registration_router
from src.shopim.handlers.user.reviews import router as user_reviews_router
from src.shopim.handlers.user.shop import router as user_shop_router
from src.shopim.handlers.user.topup import router as user_topup_router


def setup_routers(dp: Dispatcher):
    """Includes all application routers in the dispatcher.

    Admin routers are included first so they take precedence.
    """
    # Admin Routers
    dp.include_router(admin_main_menu_router)
    dp.include_router(admin_dashboard_router)
    dp.include_router(admin_user_management_router)
    dp.include_router(admin_product_management_router)
    dp.include_router(admin_product_editing_router)
    dp.include_router(admin_order_management_router)
    dp.include_router(admin_delivery_management_router)
    dp.include_router(admin_topup_management_router)
    dp.include_router(admin_warehouse_router)
    dp.include_router(admin_review_moderation_router)
    dp.include_router(admin_settings_management_router)

    # User Routers
    dp.include_router(user_registration_router)
    dp.include_router(user_profile_router)
    dp.include_router(user_shop_router)
    dp.include_router(user_reviews_router)
    dp.include_router(user_balance_router)
    dp.include_router(user_topup_router)
    dp.include_router(user_order_history_router)
