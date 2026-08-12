from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, StockMovementType
from src.shopim.keyboards.inline.admin.warehouse import (
    ProductAdjustCallback,
    WarehouseCallback,
    get_product_selection_for_adjustment_keyboard,
    get_stock_balance_keyboard,
    get_stock_movements_keyboard,
    get_warehouse_menu_keyboard,
)
from src.shopim.services.warehouse_service import WarehouseService
from src.shopim.states.admin import StockAdjustmentState


from src.shopim.filters import IsAdminFilter


router = Router(name="admin-warehouse-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

ITEMS_PER_PAGE = 10

@router.message(F.text == "📦 Sklad")
async def warehouse_menu_handler(message: types.Message):
    await message.answer(
        "Skladni boshqarish bo'limi:",
        reply_markup=get_warehouse_menu_keyboard(),
    )


@router.callback_query(WarehouseCallback.filter(F.action == "menu"))
async def back_to_warehouse_menu_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(  # type: ignore
        _("Skladni boshqarish bo'limi:"),
        reply_markup=get_warehouse_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(WarehouseCallback.filter(F.action == "stock"))
async def show_stock_balance_handler(
    callback: types.CallbackQuery,
    callback_data: WarehouseCallback,
    session: AsyncSession,
):
    service = WarehouseService(session, items_per_page=ITEMS_PER_PAGE)
    result = await service.get_products_stock(page=callback_data.page)

    text = _("Hozircha mahsulotlar mavjud emas.")
    keyboard = get_warehouse_menu_keyboard()

    if result.products:
        product_lines = []
        for product in result.products:
            alert = "⚠️" if product.stock_grams <= product.low_stock_threshold_grams else ""
            product_lines.append(
                _("<b>{product_name}</b>: {stock_grams} gr. {alert}").format(
                    product_name=product.name, stock_grams=product.stock_grams, alert=alert
                )
            )

        text = (
            f"<b>Mahsulot qoldiqlari (Sahifa {result.current_page}/{result.total_pages})</b>\n\n"
            + "\n".join(product_lines)
        )
        keyboard = get_stock_balance_keyboard(
            total_pages=result.total_pages, current_page=result.current_page
        )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore
    await callback.answer()


# --- Stock Adjustment Flow ---


async def _show_products_for_adjustment(
    callback: types.CallbackQuery, page: int, session: AsyncSession
):
    service = WarehouseService(session, items_per_page=ITEMS_PER_PAGE)
    result = await service.get_products_stock(page=page)

    text = _("Tuzatish uchun mahsulot tanlang:")
    keyboard = get_product_selection_for_adjustment_keyboard(
        products=result.products,
        total_pages=result.total_pages,
        current_page=result.current_page,
    )
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(WarehouseCallback.filter(F.action == "adjust_start"))
async def start_adjustment_handler(
    callback: types.CallbackQuery,
    callback_data: WarehouseCallback,
    session: AsyncSession,
):
    await _show_products_for_adjustment(callback, callback_data.page, session)  # type: ignore
    await callback.answer()


@router.callback_query(WarehouseCallback.filter(F.action == "adjust_product_page"))
async def paginate_adjustment_products_handler(
    callback: types.CallbackQuery,
    callback_data: WarehouseCallback,
    session: AsyncSession,
):
    await _show_products_for_adjustment(callback, callback_data.page, session)  # type: ignore
    await callback.answer()


@router.callback_query(ProductAdjustCallback.filter(F.action == "select"))
async def select_product_for_adjustment_handler(
    callback: types.CallbackQuery,
    callback_data: ProductAdjustCallback,
    state: FSMContext,
    session: AsyncSession,
):
    service = WarehouseService(session)
    product = await service.product_repo.get(callback_data.product_id)
    if not product:
        await callback.answer(_("Mahsulot topilmadi!"), show_alert=True)
        return

    await state.set_state(StockAdjustmentState.getting_grams)
    await state.update_data(
        product_id=product.id,
        product_name=product.name,
        current_stock=str(product.stock_grams),  # type: ignore
    )

    text = (  # type: ignore
        _("Mahsulot: <b>{product_name}</b>\n"
          "Joriy qoldiq: <b>{stock_grams} gramm</b>\n\n"
          "Qo'shish yoki ayirish uchun miqdorni kiriting (masalan, <b>100.5</b> yoki <b>-50</b>).").format(
            product_name=product.name, stock_grams=product.stock_grams
        )
    )
    await callback.message.edit_text(text, parse_mode="HTML")  # type: ignore
    await callback.answer()


@router.message(StockAdjustmentState.getting_grams)
async def get_adjustment_grams_handler(message: types.Message, state: FSMContext):
    try:
        grams = Decimal(message.text.replace(",", "."))
    except (InvalidOperation, ValueError):
        await message.answer(_("Xato. Miqdorni raqamda kiriting (masalan, 100.5 yoki -50)."))  # type: ignore
        return

    state_data = await state.get_data()
    current_stock = Decimal(state_data.get("current_stock", "0"))

    if current_stock + grams < 0:
        await message.answer(  # type: ignore
            _("Xato. Skladdagi qoldiq ({current_stock} gr) manfiy bo'lib qolishi mumkin emas. Boshqa miqdor kiriting.").format(
                current_stock=current_stock
            )
        )
        return

    await state.update_data(grams_to_adjust=str(grams))
    await state.set_state(StockAdjustmentState.getting_reason)
    await message.answer(_("Miqdor qabul qilindi. Endi ushbu o'zgarish sababini yozing:"))  # type: ignore


@router.message(StockAdjustmentState.getting_reason)
async def get_adjustment_reason_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, admin: Admin
):
    reason = message.text
    if not reason or len(reason) < 5:
        await message.answer(_("Iltimos, sababni to'liqroq yozing (kamida 5 belgi)."))  # type: ignore
        return

    state_data = await state.get_data()
    product_id = state_data.get("product_id")
    product_name = state_data.get("product_name")
    grams = Decimal(state_data.get("grams_to_adjust"))

    await state.clear()

    service = WarehouseService(session)
    updated_product = await service.adjust_stock(
        product_id=product_id, grams=grams, reason=reason, admin_id=admin.id
    )

    if updated_product:
        await message.answer(  # type: ignore
            _("✅ Muvaffaqiyatli!\n\n"
              "Mahsulot: <b>{product_name}</b>\n"
              "O'zgarish: <b>{grams:+} gr</b>\n"
              "Yangi qoldiq: <b>{new_stock_grams} gr</b>\n"
              "Sabab: {reason}").format(
                product_name=product_name, grams=grams, new_stock_grams=updated_product.stock_grams, reason=reason
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(_("❌ Xatolik yuz berdi. Skladni yangilab bo'lmadi."))  # type: ignore


@router.callback_query(WarehouseCallback.filter(F.action == "movements"))
async def show_stock_movements_handler(
    callback: types.CallbackQuery,
    callback_data: WarehouseCallback,
    session: AsyncSession,
):
    service = WarehouseService(session, items_per_page=ITEMS_PER_PAGE)
    result = await service.get_stock_movements(page=callback_data.page)

    text = _("Sklad bo'yicha harakatlar mavjud emas.")
    keyboard = get_warehouse_menu_keyboard()

    if result.movements:
        movement_lines = []
        for movement in result.movements:
            sign = "+" if "IN" in movement.type.name else "-"
            movement_type_str = MOVEMENT_TYPE_MAP.get(movement.type, _("Noma'lum"))
            product_name = movement.product.name if movement.product else _("O'chirilgan mahsulot")

            movement_lines.append(  # type: ignore
                _("{created_at} | {product_name} | {movement_type}: <b>{sign}{grams} gr.</b>").format(
                    created_at=movement.created_at.strftime('%d.%m %H:%M'), product_name=product_name,
                    movement_type=movement_type_str, sign=sign, grams=movement.grams
                )
            )

        text = (
            f"<b>Sklad harakatlari (Sahifa {result.current_page}/{result.total_pages})</b>\n\n"
            + "\n".join(movement_lines)
        )
        keyboard = get_stock_movements_keyboard(
            total_pages=result.total_pages, current_page=result.current_page
        )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore
    await callback.answer()