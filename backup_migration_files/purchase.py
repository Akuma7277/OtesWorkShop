from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import User, UserStatus
from src.shopim.db.repositories.balance_repository import BalanceRepository
from src.shopim.keyboards.inline.catalog import PurchaseCallback
from src.shopim.keyboards.inline.purchase import (
    PurchaseConfirmationCallback,
    get_purchase_confirmation_keyboard,
)
from src.shopim.services.catalog_service import CatalogService
from src.shopim.services.order_service import OrderCreationError, OrderService
from src.shopim.services.notification_service import NotificationService
from src.shopim.states.purchase import PurchaseStates


class IsApprovedUserFilter:
    def __call__(self, user: Optional[User]) -> bool:
        return user is not None and user.status == UserStatus.APPROVED


router = Router(name="purchase-router")
router.callback_query.filter(IsApprovedUserFilter())
router.message.filter(IsApprovedUserFilter())


@router.callback_query(PurchaseCallback.filter(F.action == "start"))
async def start_purchase_handler(
    callback: types.CallbackQuery,
    callback_data: PurchaseCallback,
    state: FSMContext,
    session: AsyncSession,
):
    service = CatalogService(session)
    product = await service.get_product_by_id(callback_data.product_id)

    if not product or product.stock_grams <= 0:
        await callback.answer(_("Afsuski, bu mahsulot hozirda mavjud emas."), show_alert=True)
        return

    await state.clear()
    await state.set_state(PurchaseStates.getting_grams)
    await state.update_data(product_id=product.id)

    text = (
        _("Siz '{product_name}' mahsulotini tanladingiz.\n"
          "Narxi: {price_per_gram} so'm / gramm.\n\n"
          "Iltimos, qancha gramm xarid qilmoqchi ekanligingizni kiriting (masalan, 50 yoki 12.5).").format(
            product_name=product.name, price_per_gram=product.sale_price_per_gram
        )
    )

    await callback.message.edit_text(text)
    await callback.answer()


@router.message(PurchaseStates.getting_grams)
async def get_grams_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User
):
    try:
        grams = Decimal(message.text.replace(",", "."))
        if grams <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        await message.answer(  # type: ignore
            _("Iltimos, miqdorni to'g'ri raqamda kiriting (masalan, 50 yoki 12.5).")
        )
        return

    state_data = await state.get_data()
    product_id = state_data.get("product_id")

    catalog_service = CatalogService(session)  # type: ignore
    product = await catalog_service.get_product_by_id(product_id)  # type: ignore

    if not product:
        await state.clear()
        await message.answer(  # type: ignore
            _("Xatolik yuz berdi. Mahsulot topilmadi. Iltimos, boshidan boshlang.")
        )
        return

    if grams > product.stock_grams:
        await message.answer(  # type: ignore
            _("Afsuski, omborda faqat {stock_grams} gramm qolgan. Iltimos, kamroq miqdor kiriting.").format(
                stock_grams=product.stock_grams
            )
        )
        return

    total_price = grams * Decimal(str(product.sale_price_per_gram))

    balance_repo = BalanceRepository(session)
    current_balance = await balance_repo.get_user_balance(user.id)
    is_balance_sufficient = current_balance >= total_price

    await state.update_data(
        grams=str(grams),
        total_price=str(total_price),
        product_name=product.name,
    )
    await state.set_state(PurchaseStates.confirming_purchase)

    balance_after = current_balance - total_price

    text = (
        _("<b>Buyurtmani tasdiqlash</b>\n\n"
          "Mahsulot: <b>{product_name}</b>\n"
          "Miqdor: <b>{grams} gramm</b>\n"
          "Jami narx: <b>{total_price:.2f} so'm</b>\n\n"
          "Joriy balans: {current_balance:.2f} so'm\n").format(
            product_name=product.name, grams=grams, total_price=total_price, current_balance=current_balance
        )
    )
    if is_balance_sufficient:
        text += _("Xariddan keyingi balans: {balance_after:.2f} so'm").format(balance_after=balance_after)
    else:
        text += (
            _("❗️<b>Balansingizda mablag' yetarli emas!</b>\n"
              "Yetishmayotgan summa: {missing_amount:.2f} so'm").format(
                missing_amount=(total_price - current_balance)
            )
        )

    await message.answer(  # type: ignore
        text,
        reply_markup=get_purchase_confirmation_keyboard(is_balance_sufficient),
        parse_mode="HTML",
    )


@router.callback_query(
    PurchaseStates.confirming_purchase,
    PurchaseConfirmationCallback.filter(F.action == "confirm"),
)
async def confirm_purchase_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    bot: Bot,
):
    try:
        state_data = await state.get_data()

        product_id = state_data.get("product_id")
        grams = Decimal(state_data.get("grams", "0"))
        total_price = Decimal(state_data.get("total_price", "0"))

        if not all([product_id, grams > 0, total_price > 0]):
            raise OrderCreationError(_("Buyurtma ma'lumotlari to'liq emas."))

        order_service = OrderService(session)
        new_order = await order_service.create_order(
            user=user,
            product_id=product_id,
            grams=grams,
            total_price=total_price,
        )

        await state.clear()
        notification_service = NotificationService(bot, session)
        await notification_service.notify_admins_of_new_order(new_order)
        await callback.message.edit_text(  # type: ignore
            _("✅ Buyurtmangiz (№{order_number}) qabul qilindi va tasdiqlash uchun adminga yuborildi.").format(
                order_number=new_order.order_number
            )
        )

    except OrderCreationError as e:
        await state.clear()
        await callback.message.edit_text(_("❌ Xatolik: {error_message}\n\nIltimos, qaytadan urinib ko'ring.").format(error_message=e))  # type: ignore
    except Exception:
        # In a real app, you should log the full exception `e`
        await state.clear()
        await callback.message.edit_text(_("❌ Noma'lum xatolik yuz berdi. Iltimos, adminga xabar bering."))  # type: ignore
    finally:
        await callback.answer()


@router.callback_query(
    PurchaseStates.confirming_purchase,
    PurchaseConfirmationCallback.filter(F.action == "cancel"),
)
async def cancel_purchase_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(_("❌ Xarid bekor qilindi."))  # type: ignore
    await callback.answer()