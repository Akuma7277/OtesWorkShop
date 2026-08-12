"""
Shopim Telegram Mini App — FastAPI backend
Runs alongside the Telegram bot, exposes /api/* endpoints.
Authentication: Telegram WebApp initData (HMAC-SHA256 validated).
"""
import hashlib
import hmac
import json
import os
import urllib.parse
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.shopim.core.config import get_settings
from src.shopim.db.models import (
    Admin,
    Category,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    Review,
    ReviewStatus,
    Topup,
    TopupStatus,
    User,
    UserStatus,
    BalanceTransaction,
    BalanceTxType,
    StockMovement,
    StockMovementType,
    DeliveryEvent,
)
from src.shopim.db.repositories.balance_repository import BalanceRepository
from src.shopim.db.repositories.product_repository import ProductRepository
from src.shopim.services.dashboard_service import DashboardService
from src.shopim.services.delivery_service import DeliveryService
from src.shopim.services.order_history_service import OrderHistoryService
from src.shopim.services.order_management_service import OrderManagementService
from src.shopim.services.topup_management_service import TopupManagementService
from src.shopim.services.user_management_service import UserManagementService

settings = get_settings()

# ──────────────────────────────────────────────
# DB setup
# ──────────────────────────────────────────────
engine = create_async_engine(settings.db_url, echo=False, pool_pre_ping=True)
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


# ──────────────────────────────────────────────
# App lifespan
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for SQLite
    if "sqlite" in settings.db_url:
        from src.shopim.db.models.all_models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Shopim Mini App API",
    description="REST API for Shopim Telegram Mini App",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Auth helpers
# ──────────────────────────────────────────────
def _validate_init_data(init_data: str, bot_token: str) -> Optional[dict]:
    """Validate Telegram WebApp initData HMAC."""
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return None
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, received_hash):
            return None
        user_json = parsed.get("user")
        if user_json:
            return json.loads(user_json)
        return {}
    except Exception:
        return None


async def get_current_telegram_id(
    x_telegram_init_data: str = Header(default=""),
) -> int:
    """Extract and validate the Telegram user ID from initData."""
    if not x_telegram_init_data:
        # Dev mode: allow passing telegram_id directly via header
        dev_id = os.getenv("DEV_TELEGRAM_ID")
        if dev_id:
            return int(dev_id)
        raise HTTPException(status_code=401, detail="Telegram initData missing")

    tg_user = _validate_init_data(x_telegram_init_data, settings.bot_token)
    if tg_user is None:
        raise HTTPException(status_code=401, detail="Invalid Telegram initData")

    user_id = tg_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="No user ID in initData")
    return int(user_id)


async def get_current_user(
    telegram_id: int = Depends(get_current_telegram_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        # Auto-create and approve user
        from src.shopim.db.models import UserStatus
        user = User(
            telegram_id=telegram_id,
            full_name="Foydalanuvchi",
            address="Toshkent",
            age=20,
            status=UserStatus.APPROVED,
            language_code="uz",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif user.status == UserStatus.BLOCKED:
        raise HTTPException(status_code=403, detail="Your account is blocked.")
    return user


async def get_current_admin(
    telegram_id: int = Depends(get_current_telegram_id),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    from src.shopim.db.models import AdminRole
    stmt = select(Admin).where(Admin.telegram_id == telegram_id)
    admin = (await db.execute(stmt)).scalar_one_or_none()

    if telegram_id in settings.super_admins_list:
        if not admin:
            admin = Admin(
                telegram_id=telegram_id,
                full_name="Super Admin",
                role=AdminRole.SUPER_ADMIN,
                is_active=True,
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
        elif not admin.is_active or admin.role != AdminRole.SUPER_ADMIN:
            admin.is_active = True
            admin.role = AdminRole.SUPER_ADMIN
            await db.commit()
            await db.refresh(admin)
        return admin

    if not admin or not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return admin


def _is_admin_telegram_id(telegram_id: int) -> bool:
    return telegram_id in settings.super_admins_list


# ──────────────────────────────────────────────
# Helper: check if user is admin (lightweight)
# ──────────────────────────────────────────────
async def _user_is_admin(telegram_id: int, db: AsyncSession) -> bool:
    from src.shopim.db.models import AdminRole
    if telegram_id in settings.super_admins_list:
        stmt = select(Admin).where(Admin.telegram_id == telegram_id)
        admin = (await db.execute(stmt)).scalar_one_or_none()
        if not admin:
            admin = Admin(
                telegram_id=telegram_id,
                full_name="Super Admin",
                role=AdminRole.SUPER_ADMIN,
                is_active=True,
            )
            db.add(admin)
            await db.commit()
        elif not admin.is_active or admin.role != AdminRole.SUPER_ADMIN:
            admin.is_active = True
            admin.role = AdminRole.SUPER_ADMIN
            await db.commit()
        return True

    stmt = select(Admin).where(Admin.telegram_id == telegram_id, Admin.is_active == True)
    return (await db.execute(stmt)).scalar_one_or_none() is not None




# ──────────────────────────────────────────────
# Routes: Users / Profile
# ──────────────────────────────────────────────
@app.get("/api/users/me")
async def get_me(
    user: User = Depends(get_current_user),
    telegram_id: int = Depends(get_current_telegram_id),
    db: AsyncSession = Depends(get_db),
):
    bal_repo = BalanceRepository(db)
    balance = await bal_repo.get_user_balance(user.id)
    is_admin = await _user_is_admin(telegram_id, db)
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "full_name": user.full_name,
        "username": user.username,
        "phone": user.phone,
        "address": user.address,
        "age": user.age,
        "status": user.status.value,
        "language_code": user.language_code,
        "created_at": user.created_at.isoformat(),
        "is_admin": is_admin,
        "balance": float(balance),
    }


@app.patch("/api/users/me")
async def update_me(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    allowed = {"address", "language_code"}
    for k, v in data.items():
        if k in allowed and hasattr(user, k):
            setattr(user, k, v)
    await db.commit()
    return {"ok": True}


# ──────────────────────────────────────────────
# Routes: Balance
# ──────────────────────────────────────────────
@app.get("/api/balance/me")
async def get_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bal_repo = BalanceRepository(db)
    balance = await bal_repo.get_user_balance(user.id)
    return {"balance": float(balance)}


# ──────────────────────────────────────────────
# Routes: Categories
# ──────────────────────────────────────────────
@app.get("/api/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(Category).where(Category.is_active == True).order_by(Category.name)
    cats = (await db.execute(stmt)).scalars().all()
    return [{"id": c.id, "name": c.name} for c in cats]


# ──────────────────────────────────────────────
# Routes: Products
# ──────────────────────────────────────────────
@app.get("/api/debug")
async def get_debug_info(request: Request):
    import os
    # Exclude sensitive secrets like database password or bot token
    safe_env = {
        k: v for k, v in os.environ.items()
        if not any(secret in k.lower() for secret in ("token", "password", "key", "secret", "url"))
    }
    # Capture all headers safely
    safe_headers = {
        k: v for k, v in request.headers.items()
        if not any(secret in k.lower() for secret in ("authorization", "cookie", "token"))
    }
    return {
        "railway_public_domain_env": os.getenv("RAILWAY_PUBLIC_DOMAIN"),
        "railway_static_url_env": os.getenv("RAILWAY_STATIC_URL"),
        "settings_mini_app_url": settings.mini_app_url,
        "resolved_get_mini_app_url": settings.get_mini_app_url,
        "env_keys": list(safe_env.keys()),
        "safe_env": safe_env,
        "request_headers": safe_headers,
    }



@app.get("/api/debug-auth")
async def debug_auth(request: Request, db: AsyncSession = Depends(get_db)):
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if not init_data:
        return {"error": "X-Telegram-Init-Data header is missing"}
    import urllib.parse, json, hmac, hashlib
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
        received_hash = parsed.pop("hash", None)
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        hash_match = hmac.compare_digest(expected, received_hash) if received_hash else False
        return {
            "init_data_length": len(init_data),
            "parsed_keys": list(parsed.keys()),
            "received_hash": received_hash,
            "expected_hash": expected,
            "hash_match": hash_match,
            "bot_token_configured": bool(settings.bot_token),
            "user": json.loads(parsed.get("user", "{}")) if parsed.get("user") else None
        }
    except Exception as e:
        return {"error": str(e)}


def _product_dict(p: Product) -> dict:

    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "image_url": p.image_url,
        "sale_price_per_gram": float(p.sale_price_per_gram),
        "cost_price_per_gram": float(p.cost_price_per_gram),
        "stock_grams": float(p.stock_grams),
        "is_active": p.is_active,
        "category_id": p.category_id,
    }


@app.get("/api/products")
async def list_products(
    is_active: bool = True,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product).where(Product.is_active == is_active)
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    if search:
        stmt = stmt.where(Product.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Product.name).offset(offset).limit(limit)
    products = (await db.execute(stmt)).scalars().all()
    return [_product_dict(p) for p in products]


@app.get("/api/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(Product, product_id)
    if not p or not p.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_dict(p)


# ──────────────────────────────────────────────
# Routes: Orders
# ──────────────────────────────────────────────
def _order_dict(order: Order) -> dict:
    items = []
    for item in (order.items or []):
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name_snapshot": item.product_name_snapshot,
            "grams": float(item.grams),
            "unit_price_per_gram": float(item.unit_price_per_gram),
            "subtotal": float(item.subtotal),
        })
    events = []
    for ev in (order.delivery_events or []):
        events.append({
            "id": ev.id,
            "status": ev.status,
            "note": ev.note,
            "created_at": ev.created_at.isoformat(),
        })
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status.value,
        "total_amount": float(order.total_amount),
        "delivery_address": order.delivery_address,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
        "rejection_reason": order.rejection_reason,
        "admin_note": order.admin_note,
        "items": items,
        "delivery_events": events,
    }


@app.get("/api/orders/me")
async def get_my_orders(
    user: User = Depends(get_current_user),
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    service = OrderHistoryService(db, orders_per_page=per_page)
    result = await service.get_user_orders(user.id, page=page)
    orders = result.orders
    if status:
        try:
            s = OrderStatus(status)
            orders = [o for o in orders if o.status == s]
        except ValueError:
            pass
    return {
        "items": [_order_dict(o) for o in orders],
        "total_pages": result.total_pages,
        "current_page": result.current_page,
    }


@app.get("/api/orders/{order_id}")
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderHistoryService(db)
    order = await service.get_order_details(order_id, user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _order_dict(order)


@app.post("/api/orders", status_code=201)
async def place_order(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.status != UserStatus.APPROVED:
        raise HTTPException(status_code=403, detail="Your account is not approved yet.")

    data = await request.json()
    items_data = data.get("items", [])
    delivery_address = data.get("delivery_address", "").strip()

    if not items_data:
        raise HTTPException(status_code=400, detail="No items in order")
    if not delivery_address:
        raise HTTPException(status_code=400, detail="Delivery address required")

    # Check balance
    bal_repo = BalanceRepository(db)
    balance = await bal_repo.get_user_balance(user.id)

    order_items = []
    total = 0.0

    for item in items_data:
        product = await db.get(Product, item["product_id"])
        if not product or not product.is_active:
            raise HTTPException(status_code=400, detail=f"Product {item['product_id']} not found")
        grams = float(item["grams"])
        if product.stock_grams < grams:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")
        subtotal = grams * float(product.sale_price_per_gram)
        total += subtotal
        order_items.append((product, grams, subtotal))

    if balance < total:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Need {total:.0f}, have {float(balance):.0f}")

    import uuid, datetime as dt
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order = Order(
        order_number=order_number,
        user_id=user.id,
        status=OrderStatus.PENDING_ADMIN,
        total_amount=total,
        delivery_address=delivery_address,
    )
    db.add(order)
    await db.flush()

    for product, grams, subtotal in order_items:
        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name_snapshot=product.name,
            grams=grams,
            unit_price_per_gram=float(product.sale_price_per_gram),
            cost_price_per_gram_snapshot=float(product.cost_price_per_gram),
            subtotal=subtotal,
        )
        db.add(oi)
        # Deduct stock
        product.stock_grams = float(product.stock_grams) - grams
        db.add(StockMovement(
            product_id=product.id,
            type=StockMovementType.SALE_OUT,
            grams=grams,
            stock_before=float(product.stock_grams) + grams,
            stock_after=float(product.stock_grams),
            reference_type="Order",
            reference_id=order.id,
        ))

    # Deduct balance
    balance_after = float(balance) - total
    db.add(BalanceTransaction(
        user_id=user.id,
        type=BalanceTxType.PURCHASE,
        amount=total,
        balance_before=float(balance),
        balance_after=balance_after,
        reference_type="Order",
        reference_id=order.id,
    ))

    await db.commit()
    await db.refresh(order)
    return {"id": order.id, "order_number": order.order_number, "status": order.status.value, "total_amount": float(order.total_amount)}


@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_ADMIN:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled at this stage")

    order.status = OrderStatus.CANCELLED

    # Refund balance
    bal_repo = BalanceRepository(db)
    balance = await bal_repo.get_user_balance(user.id)
    db.add(BalanceTransaction(
        user_id=user.id,
        type=BalanceTxType.REFUND,
        amount=float(order.total_amount),
        balance_before=float(balance),
        balance_after=float(balance) + float(order.total_amount),
        reference_type="Order",
        reference_id=order.id,
        note="Buyurtma bekor qilindi",
    ))

    await db.commit()
    return {"ok": True}


# ──────────────────────────────────────────────
# Routes: Topups
# ──────────────────────────────────────────────
@app.post("/api/topups", status_code=201)
async def create_topup(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    amount = float(data.get("amount", 0))
    if amount < settings.min_topup_amount:
        raise HTTPException(status_code=400, detail=f"Minimum topup: {settings.min_topup_amount:.0f}")
    topup = Topup(
        user_id=user.id,
        amount=amount,
        payment_method=data.get("payment_method", "manual"),
        receipt_file_id=data.get("receipt_file_id"),
        status=TopupStatus.PENDING,
    )
    db.add(topup)
    await db.commit()
    return {"id": topup.id, "status": "PENDING"}


# ──────────────────────────────────────────────
# Routes: Reviews
# ──────────────────────────────────────────────
@app.get("/api/reviews")
async def list_reviews(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Review)
        .where(Review.status == ReviewStatus.APPROVED)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    reviews = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "rating": r.rating,
            "text": r.text,
            "created_at": r.created_at.isoformat(),
            "user_name": r.user.full_name if r.user else "—",
        }
        for r in reviews
    ]


@app.post("/api/reviews", status_code=201)
async def post_review(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    rating = max(1, min(5, int(data.get("rating", 5))))
    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Review text required")
    review = Review(user_id=user.id, rating=rating, text=text, status=ReviewStatus.PENDING)
    db.add(review)
    await db.commit()
    return {"id": review.id, "status": "PENDING"}


# ──────────────────────────────────────────────
# Admin Routes
# ──────────────────────────────────────────────
@app.get("/api/admin/dashboard")
async def admin_dashboard(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    stats = await service.get_stats()
    return {
        "orders_today_count": stats.orders_today_count,
        "revenue_today": float(stats.revenue_today),
        "profit_today": float(stats.profit_today),
        "total_orders_count": stats.total_orders_count,
        "total_revenue": float(stats.total_revenue),
        "pending_registrations_count": stats.pending_registrations_count,
        "pending_topups_count": stats.pending_topups_count,
        "pending_orders_count": stats.pending_orders_count,
        "active_users_count": stats.active_users_count,
        "low_stock_products_count": stats.low_stock_products_count,
    }


@app.get("/api/admin/orders")
async def admin_list_orders(
    status: Optional[str] = None,
    per_page: int = 20,
    page: int = 1,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    stmt = select(Order).options(selectinload(Order.items), selectinload(Order.user))
    if status:
        try:
            stmt = stmt.where(Order.status == OrderStatus(status))
        except ValueError:
            pass
    stmt = stmt.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    orders = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {**_order_dict(o), "user": {"full_name": o.user.full_name if o.user else "—", "telegram_id": o.user.telegram_id if o.user else None}}
            for o in orders
        ]
    }


@app.post("/api/admin/orders/{order_id}/approve")
async def admin_approve_order(
    order_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = OrderManagementService(db)
    order = await service.approve_order(order_id, admin)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot approve this order")
    return {"ok": True, "status": order.status.value}


@app.post("/api/admin/orders/{order_id}/reject")
async def admin_reject_order(
    order_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    reason = data.get("reason", "Admin tomonidan rad etildi")
    service = OrderManagementService(db)
    order = await service.reject_order(order_id, admin, reason)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot reject this order")
    return {"ok": True}


@app.post("/api/admin/orders/{order_id}/delivery")
async def admin_set_delivery(
    order_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    try:
        new_status = OrderStatus[data["status"]]
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid status")
    service = DeliveryService(db)
    order = await service.update_delivery_status(order_id, new_status, admin)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot update delivery status")
    return {"ok": True, "status": order.status.value}


@app.get("/api/admin/topups/pending")
async def admin_pending_topups(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Topup)
        .where(Topup.status == TopupStatus.PENDING)
        .options(selectinload(Topup.user))
        .order_by(Topup.created_at.desc())
    )
    topups = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "user_name": t.user.full_name if t.user else "Foydalanuvchi",
            "amount": float(t.amount),
            "payment_method": t.payment_method,
            "receipt_file_id": t.receipt_file_id,
            "created_at": t.created_at.isoformat(),
        }
        for t in topups
    ]



@app.post("/api/admin/topups/{topup_id}/approve")
async def admin_approve_topup(
    topup_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = TopupManagementService(db)
    topup = await service.approve_topup(topup_id, admin)
    if not topup:
        raise HTTPException(status_code=400, detail="Cannot approve topup")
    return {"ok": True}


@app.post("/api/admin/topups/{topup_id}/reject")
async def admin_reject_topup(
    topup_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    service = TopupManagementService(db)
    topup = await service.reject_topup(topup_id, admin, data.get("note", ""))
    if not topup:
        raise HTTPException(status_code=400, detail="Cannot reject topup")
    return {"ok": True}


@app.get("/api/admin/users")
async def admin_list_users(
    status: Optional[str] = None,
    per_page: int = 20,
    page: int = 1,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User)
    if status:
        try:
            stmt = stmt.where(User.status == UserStatus(status))
        except ValueError:
            pass
    stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    users = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "full_name": u.full_name,
                "username": u.username,
                "phone": u.phone,
                "address": u.address,
                "age": u.age,
                "status": u.status.value,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
    }


@app.post("/api/admin/users/{user_id}/approve")
async def admin_approve_user(
    user_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserManagementService(db)
    user = await service.approve_user(user_id, admin)
    if not user:
        raise HTTPException(status_code=400, detail="Cannot approve user")
    return {"ok": True}


@app.post("/api/admin/users/{user_id}/reject")
async def admin_reject_user(
    user_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await request.json()
    service = UserManagementService(db)
    user = await service.reject_user(user_id, admin, data.get("reason", ""))
    if not user:
        raise HTTPException(status_code=400, detail="Cannot reject user")
    return {"ok": True}


@app.post("/api/admin/users/{user_id}/block")
async def admin_block_user(
    user_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.BLOCKED
    await db.commit()
    return {"ok": True}


@app.post("/api/admin/users/{user_id}/unblock")
async def admin_unblock_user(
    user_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.APPROVED
    await db.commit()
    return {"ok": True}


# ──────────────────────────────────────────────
# Admin Product Management Routes
# ──────────────────────────────────────────────
@app.post("/api/admin/products", status_code=201)
async def admin_create_product(
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from src.shopim.services.product_management_service import ProductManagementService
    data = await request.json()
    service = ProductManagementService(db)
    product = await service.create_product(data, admin.id)
    return _product_dict(product)


@app.patch("/api/admin/products/{product_id}")
async def admin_update_product(
    product_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from src.shopim.services.product_management_service import ProductManagementService
    data = await request.json()
    service = ProductManagementService(db)
    product = await service.update_product(product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_dict(product)


@app.delete("/api/admin/products/{product_id}")
async def admin_delete_product(
    product_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from src.shopim.services.product_management_service import ProductManagementService
    service = ProductManagementService(db)
    success = await service.delete_product(product_id)
    if not success:
        # If product cannot be hard deleted, deactivate it instead
        product = await db.get(Product, product_id)
        if product:
            product.is_active = False
            await db.commit()
            return {"ok": True, "message": "Product deactivated"}
        raise HTTPException(status_code=400, detail="Cannot delete or deactivate product")
    return {"ok": True, "message": "Product deleted"}


# ──────────────────────────────────────────────
# Admin Reviews Moderation
# ──────────────────────────────────────────────
@app.get("/api/admin/reviews/pending")
async def admin_list_pending_reviews(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Review)
        .where(Review.status == ReviewStatus.PENDING)
        .options(selectinload(Review.user))
        .order_by(Review.created_at.desc())
    )
    reviews = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "rating": r.rating,
            "text": r.text,
            "created_at": r.created_at.isoformat(),
            "user": {
                "full_name": r.user.full_name if r.user else "—",
                "telegram_id": r.user.telegram_id if r.user else None,
            }
        }
        for r in reviews
    ]


@app.post("/api/admin/reviews/{review_id}/approve")
async def admin_approve_review(
    review_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.status = ReviewStatus.APPROVED
    await db.commit()
    return {"ok": True}


@app.post("/api/admin/reviews/{review_id}/reject")
async def admin_reject_review(
    review_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.status = ReviewStatus.REJECTED
    await db.commit()
    return {"ok": True}


# ──────────────────────────────────────────────
# Admin Settings Management
# ──────────────────────────────────────────────
@app.get("/api/admin/settings")
async def admin_get_settings(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from src.shopim.services.settings_service import SettingsService
    service = SettingsService(db)
    settings_model = await service.get_bot_settings()
    return settings_model.model_dump(mode="json")


@app.patch("/api/admin/settings")
async def admin_update_settings(
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from src.shopim.services.settings_service import SettingsService
    data = await request.json()
    service = SettingsService(db)
    updated = await service.update_bot_settings(data, admin.id)
    return updated.model_dump(mode="json")



# ──────────────────────────────────────────────
# Serve built Mini App static files
# ──────────────────────────────────────────────
# api.py is at src/shopim/api.py
# webapp dist is at src/webapp/dist
_here = os.path.dirname(os.path.abspath(__file__))            # .../src/shopim
_static_dir = os.path.normpath(os.path.join(_here, "..", "webapp", "dist"))  # .../src/webapp/dist

if os.path.isdir(_static_dir):
    from fastapi.responses import FileResponse

    # Mount /assets only if the subfolder exists (Vite puts JS/CSS there)
    _assets_dir = os.path.join(_static_dir, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve React SPA — always return index.html for unknown routes (client-side routing)."""
        # Try to serve a real file first (e.g., favicon.ico, manifest.json)
        requested = os.path.join(_static_dir, full_path)
        if full_path and os.path.isfile(requested):
            return FileResponse(requested)
        index = os.path.join(_static_dir, "index.html")
        return FileResponse(index)

else:
    @app.get("/")
    async def root():
        return {
            "message": "Shopim Mini App API is running.",
            "hint": "Build the frontend: cd src/webapp && npm install && npm run build",
            "mini_app_url": settings.get_mini_app_url,
        }

