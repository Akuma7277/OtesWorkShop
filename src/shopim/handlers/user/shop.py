import uuid
from decimal import Decimal

from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Category, Order, OrderItem, OrderStatus, Product, User
from src.shopim.filters import IsApprovedUserFilter
from src.shopim.keyboards.reply.main_menu import get_user_main_keyboard
from src.shopim.services.settings_service import SettingsService

router = Router(name="user-shop-router")
router.message.filter(IsApprovedUserFilter())


# --- Callback Data ---
class CategorySelectCallback(CallbackData, prefix="cat_sel"):
    category_id: int


class SubcategorySelectCallback(CallbackData, prefix="subcat_sel"):
    category_id: int
    subcategory_id: int


class ProductSelectCallback(CallbackData, prefix="prod_sel"):
    product_id: int


class PaymentMethodCallback(CallbackData, prefix="pay_method"):
    product_id: int
    method: str


class OrderActionCallback(CallbackData, prefix="ord_act"):
    order_id: int
    action: str


# --- Start Buy Flow ---
@router.message(
    F.text.in_({"Купить", "Sotib olish", "🛒 Kuput", "🛒 Купить", "🛒 Sotib olish"}),
    StateFilter("*"),
)
async def start_buy_flow_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User
):
    await state.clear()
    stmt = select(Category).where(Category.is_active.is_(True)).order_by(Category.name)
    result = await session.execute(stmt)
    categories = result.scalars().all()

    if not categories:
        empty_msg = _("Afsuski, hozircha mavjud joylashuvlar yo'q.")
        await message.answer(empty_msg, reply_markup=get_user_main_keyboard())
        return

    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat.name, callback_data=CategorySelectCallback(category_id=cat.id).pack()
        )
    builder.adjust(1)

    prompt = _("Joylash joyini (Toshkent tumanini) tanlang:")
    await message.answer(prompt, reply_markup=builder.as_markup())


@router.callback_query(CategorySelectCallback.filter())
async def select_category_handler(
    callback: types.CallbackQuery,
    callback_data: CategorySelectCallback,
    session: AsyncSession,
    user: User,
):
    stmt = (
        select(Product)
        .where(Product.category_id == callback_data.category_id)
        .where(Product.is_active.is_(True))
        .where(Product.stock_grams > 0)
    )
    result = await session.execute(stmt)
    products = result.scalars().all()

    if not products:
        no_prod_msg = _("Ushbu tumanda hozircha tovarlar mavjud emas.")
        await callback.answer(no_prod_msg, show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for prod in products:
        button_text = f"📍 {prod.name} ({prod.sale_price_per_gram:.2f} USD)"
        builder.button(
            text=button_text,
            callback_data=ProductSelectCallback(product_id=prod.id).pack(),
        )

    builder.button(
        text=_("⬅️ Orqaga"),
        callback_data="back_to_categories",
    )
    builder.adjust(1)

    prompt = _("Ushbu tumandagi mahsulotni tanlang:")
    await callback.message.edit_text(prompt, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_handler(
    callback: types.CallbackQuery, session: AsyncSession, user: User
):
    stmt = select(Category).where(Category.is_active.is_(True)).order_by(Category.name)
    result = await session.execute(stmt)
    categories = result.scalars().all()

    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat.name, callback_data=CategorySelectCallback(category_id=cat.id).pack()
        )
    builder.adjust(1)

    prompt = _("Joylash joyini (Toshkent tumanini) tanlang:")
    await callback.message.edit_text(prompt, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(
    callback: types.CallbackQuery, state: FSMContext, user: User
):
    await state.clear()
    await callback.message.answer(
        _("Asosiy menyu:"),
        reply_markup=get_user_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(ProductSelectCallback.filter())
async def select_product_handler(
    callback: types.CallbackQuery,
    callback_data: ProductSelectCallback,
    session: AsyncSession,
    user: User,
):
    product = await session.get(Product, callback_data.product_id)

    if not product or not product.is_active:
        not_found_msg = _("Mahsulot topilmadi yoki tugagan.")
        await callback.answer(not_found_msg, show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.button(
        text="💰 LTC (Litecoin)",
        callback_data=PaymentMethodCallback(product_id=product.id, method="LTC").pack(),
    )
    builder.button(
        text="💵 USDT (TRC20)",
        callback_data=PaymentMethodCallback(product_id=product.id, method="USDT").pack(),
    )
    builder.button(
        text=_("⬅️ Orqaga"),
        callback_data="back_to_categories",
    )
    builder.adjust(2, 1)

    text = _("To'lov uchun: <b>{price:.2f} USD</b>\nTo'lov usulini tanlang:").format(price=product.sale_price_per_gram)
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(PaymentMethodCallback.filter())
async def choose_payment_method_handler(
    callback: types.CallbackQuery,
    callback_data: PaymentMethodCallback,
    user: User,
    session: AsyncSession,
):
    product = await session.get(Product, callback_data.product_id)

    if not product:
        await callback.answer(_("Mahsulot topilmadi."), show_alert=True)
        return

    settings_service = SettingsService(session)
    settings = await settings_service.get_bot_settings()

    order_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    new_order = Order(
        order_number=order_num,
        user_id=user.id,
        status=OrderStatus.PENDING_ADMIN,
        total_amount=product.sale_price_per_gram,
        delivery_address=product.pickup_address or "Toshkent shahri",
    )
    session.add(new_order)
    await session.flush()

    order_item = OrderItem(
        order_id=new_order.id,
        product_id=product.id,
        product_name_snapshot=product.name,
        grams=1.0,
        unit_price_per_gram=product.sale_price_per_gram,
        cost_price_per_gram_snapshot=product.cost_price_per_gram,
        subtotal=product.sale_price_per_gram,
    )
    session.add(order_item)
    await session.commit()

    method = callback_data.method
    wallet = (
        settings.ltc_wallet_address
        if method == "LTC"
        else settings.usdt_wallet_address
    )
    crypto_amount = (
        f"{float(product.sale_price_per_gram) / 45.0:.6f}"
        if method == "LTC"
        else f"{product.sale_price_per_gram:.2f}"
    )

    invoice_text = _(
        "To'lov uchun: <b>{price:.2f} USD</b>\n"
        "Manzil {method}:\n"
        "<code>{wallet}</code>\n"
        "Summa {method}: <b>{crypto_amount}</b>\n\n"
        "To'lov tarmoq tasdiqlangach tushadi — odatda bir necha daqiqa.\n"
        "To'lagach «To'lovni tekshirish» tugmasini bosing."
    ).format(
        price=product.sale_price_per_gram,
        method=method,
        wallet=wallet,
        crypto_amount=crypto_amount,
    )

    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("To'lovni tekshirish"),
        callback_data=OrderActionCallback(order_id=new_order.id, action="check").pack(),
    )
    builder.button(
        text=_("To'lovni bekor qilish"),
        callback_data=OrderActionCallback(order_id=new_order.id, action="cancel").pack(),
    )
    builder.button(
        text=_("⬅️ Orqaga"),
        callback_data="back_to_categories",
    )
    builder.adjust(2, 1)

    await callback.message.edit_text(invoice_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(OrderActionCallback.filter(F.action == "cancel"))
async def cancel_payment_handler(
    callback: types.CallbackQuery,
    callback_data: OrderActionCallback,
    session: AsyncSession,
    user: User,
):
    order = await session.get(Order, callback_data.order_id)
    if order:
        order.status = OrderStatus.CANCELLED
        await session.commit()

    cancel_text = _("To'lov bekor qilindi.")
    await callback.message.edit_text(cancel_text, reply_markup=None)
    await callback.answer()


@router.callback_query(OrderActionCallback.filter(F.action == "check"))
async def check_payment_handler(
    callback: types.CallbackQuery,
    callback_data: OrderActionCallback,
    user: User,
    session: AsyncSession,
    bot: Bot,
):
    order = await session.get(Order, callback_data.order_id)
    if not order:
        await callback.answer(_("Buyurtma topilmadi."), show_alert=True)
        return

    from src.shopim.services.notification_service import NotificationService
    notification_service = NotificationService(bot, session)

    alert_text = _(
        "🔔 <b>To'lov bo'yicha bildirishnoma!</b>\n"
        "Foydalanuvchi: {full_name} (@{username})\n"
        "Buyurtma №: <b>{order_number}</b>\n"
        "Summa: <b>{total_amount:.2f} USD</b>"
    ).format(
        full_name=user.full_name,
        username=user.username or "bez_username",
        order_number=order.order_number,
        total_amount=order.total_amount,
    )

    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("✅ Tasdiqlash"),
        callback_data=f"admin_approve_ord:{order.id}",
    )
    builder.button(
        text=_("❌ Rad etish"),
        callback_data=f"admin_reject_ord:{order.id}",
    )
    builder.adjust(2)

    await notification_service.notify_admins(alert_text, reply_markup=builder.as_markup())
    alert_user_text = _("To'lov admin tekshiruviga yuborildi. Tasdiqlanishini kuting.")
    await callback.answer(alert_user_text, show_alert=True)


# --- Stock Availability (Mavjud yuklar / Наличие) ---
@router.message(
    F.text.in_({"Наличие", "Mavjud yuklar", "📦 Nalichie", "📦 Наличие", "📦 Mavjud yuklar"}),
    StateFilter("*"),
)
async def show_stock_availability_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User
):
    await state.clear()
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True))
        .where(Product.stock_grams > 0)
        .order_by(Product.name)
    )
    result = await session.execute(stmt)
    products = result.scalars().all()

    if not products:
        empty_msg = _("Afsuski, hozircha omborda tovarlar mavjud emas.")
        await message.answer(empty_msg, reply_markup=get_user_main_keyboard())
        return

    lines = [_("📦 <b>Mavjud tovarlar:</b>\n")]
    for prod in products:
        lines.append(
            f"• <b>{prod.name}</b> — {prod.sale_price_per_gram:.2f} USD ({prod.stock_grams:.1f} gr {_('mavjud')})"
        )
    lines.append(_("\nXarid qilish uchun <b>«Sotib olish»</b> tugmasini bosing."))

    await message.answer("\n".join(lines), reply_markup=get_user_main_keyboard(), parse_mode="HTML")
