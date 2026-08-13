# ruff: noqa: D101, D102, D103, D104, D105, D107
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    BigInteger,
    Integer,
    JSON,
    TEXT,
    VARCHAR,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    desc,
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.sql import func

Base = declarative_base()

PK_TYPE = BigInteger().with_variant(Integer, "sqlite")



class UserStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class AdminRole(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    MANAGER = "MANAGER"


class TopupStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class OrderStatus(enum.Enum):
    DRAFT = "DRAFT"
    PENDING_ADMIN = "PENDING_ADMIN"
    APPROVED = "APPROVED"
    PACKING = "PACKING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class StockMovementType(enum.Enum):
    PURCHASE_IN = "PURCHASE_IN"
    ADJUSTMENT_IN = "ADJUSTMENT_IN"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT"
    SALE_OUT = "SALE_OUT"
    RETURN_IN = "RETURN_IN"
    DAMAGE_OUT = "DAMAGE_OUT"


class BalanceTxType(enum.Enum):
    TOPUP = "TOPUP"
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"
    MANUAL_CREDIT = "MANUAL_CREDIT"
    MANUAL_DEBIT = "MANUAL_DEBIT"


class ReviewStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(VARCHAR(255))
    full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(VARCHAR(32))
    address: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), nullable=False, default=UserStatus.PENDING
    )
    language_code: Mapped[str] = mapped_column(VARCHAR(2), nullable=False, default="uz")
    rejection_reason: Mapped[str | None] = mapped_column(TEXT)
    is_deleted: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("age IS NULL OR (age BETWEEN 13 AND 120)"),
        Index("idx_users_status", "status"),
    )


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole), nullable=False, default=AdminRole.MANAGER
    )
    language_code: Mapped[str] = mapped_column(VARCHAR(2), nullable=False, default="uz")
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(120), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    category_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("categories.id")
    )
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    slug: Mapped[str] = mapped_column(VARCHAR(300), unique=True, nullable=False)
    # Public info — visible to all users
    description: Mapped[str | None] = mapped_column(TEXT)  # legacy field kept for compat
    public_description: Mapped[str | None] = mapped_column(TEXT)
    pickup_address: Mapped[str | None] = mapped_column(TEXT)
    image_file_id: Mapped[str | None] = mapped_column(TEXT)
    image_url: Mapped[str | None] = mapped_column(TEXT)  # legacy / public image
    public_image_url: Mapped[str | None] = mapped_column(TEXT)
    # Secret info — only shown to the user who purchased, after payment approved
    secret_description: Mapped[str | None] = mapped_column(TEXT)
    secret_image_url: Mapped[str | None] = mapped_column(TEXT)
    cost_price_per_gram: Mapped[float] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    sale_price_per_gram: Mapped[float] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    stock_grams: Mapped[float] = mapped_column(
        Numeric(18, 3), nullable=False, default=0
    )
    low_stock_threshold_grams: Mapped[float] = mapped_column(
        Numeric(18, 3), nullable=False, default=100
    )
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    last_low_stock_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("admins.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    stock_movements: Mapped[list[StockMovement]] = relationship(
        "StockMovement", back_populates="product"
    )
    __table_args__ = (
        CheckConstraint("cost_price_per_gram >= 0"),
        CheckConstraint("sale_price_per_gram >= 0"),
        CheckConstraint("stock_grams >= 0"),
    )


class Topup(Base):
    __tablename__ = "topups"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
    receipt_file_id: Mapped[str | None] = mapped_column(TEXT)
    external_transaction_id: Mapped[str | None] = mapped_column(
        VARCHAR(255), unique=True
    )
    status: Mapped[TopupStatus] = mapped_column(
        Enum(TopupStatus), nullable=False, default=TopupStatus.PENDING
    )
    admin_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("admins.id"))
    admin_note: Mapped[str | None] = mapped_column(TEXT)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship("User")
    __table_args__ = (
        CheckConstraint("amount > 0"),
        Index("idx_topups_status", "status"),
    )


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    type: Mapped[BalanceTxType] = mapped_column(Enum(BalanceTxType), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    balance_before: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    balance_after: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(VARCHAR(50))
    reference_id: Mapped[int | None] = mapped_column(BIGINT)
    created_by_admin_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("admins.id")
    )
    note: Mapped[str | None] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(VARCHAR(40), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING_ADMIN
    )
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    delivery_address: Mapped[str] = mapped_column(TEXT, nullable=False)
    delivery_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assigned_admin_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("admins.id")
    )
    rejection_reason: Mapped[str | None] = mapped_column(TEXT)
    admin_note: Mapped[str | None] = mapped_column(TEXT)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Post-purchase receipt tracking
    receipt_confirmed: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    receipt_issue_reported: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship()
    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    delivery_events: Mapped[list[DeliveryEvent]] = relationship(
        "DeliveryEvent", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("total_amount > 0"),
        Index("idx_orders_status", "status"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id"), nullable=False
    )
    product_name_snapshot: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    grams: Mapped[float] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price_per_gram: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    cost_price_per_gram_snapshot: Mapped[float] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    subtotal: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    order: Mapped[Order] = relationship("Order", back_populates="items")
    product: Mapped[Product] = relationship("Product")

    __table_args__ = (CheckConstraint("grams > 0"),)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id"), nullable=False
    )
    type: Mapped[StockMovementType] = mapped_column(
        Enum(StockMovementType), nullable=False
    )
    grams: Mapped[float] = mapped_column(Numeric(18, 3), nullable=False)
    stock_before: Mapped[float] = mapped_column(Numeric(18, 3), nullable=False)
    stock_after: Mapped[float] = mapped_column(Numeric(18, 3), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(VARCHAR(50))
    reference_id: Mapped[int | None] = mapped_column(BIGINT)
    reason: Mapped[str | None] = mapped_column(TEXT)
    created_by_admin_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("admins.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    product: Mapped[Product] = relationship("Product", back_populates="stock_movements")

    __table_args__ = (
        CheckConstraint("grams > 0"),
        Index("idx_stock_product_created", "product_id", desc("created_at")),
    )


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    note: Mapped[str | None] = mapped_column(TEXT)
    created_by_admin_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("admins.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    order: Mapped[Order] = relationship("Order", back_populates="delivery_events")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    recipient_telegram_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    recipient_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    event_type: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    body: Mapped[str] = mapped_column(TEXT, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(VARCHAR(50))
    reference_id: Mapped[int | None] = mapped_column(BIGINT)
    is_sent: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (Index("idx_notifications_unsent", "is_sent", "created_at"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    actor_telegram_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    actor_role: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    action: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(VARCHAR(50))
    entity_id: Mapped[int | None] = mapped_column(BIGINT)
    old_data: Mapped[dict | None] = mapped_column(JSON)
    new_data: Mapped[dict | None] = mapped_column(JSON)
    ip_or_source: Mapped[str | None] = mapped_column(VARCHAR(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AppSettings(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(VARCHAR(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("admins.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False, default=5)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING
    )
    channel_message_id: Mapped[int | None] = mapped_column(BIGINT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship("User")


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    image_url: Mapped[str | None] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(PK_TYPE, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    sender_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)  # "USER" or "ADMIN"
    text: Mapped[str | None] = mapped_column(TEXT)
    image_url: Mapped[str | None] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship("User")


