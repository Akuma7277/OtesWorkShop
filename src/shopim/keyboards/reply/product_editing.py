from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin, Product
from src.shopim.keyboards.inline.admin.product_editing import (
    ProductEditCallback,
    ProductEditFieldCallback,
    get_back_to_edit_menu_keyboard,
    get_product_edit_menu_keyboard,
    get_product_delete_confirmation_keyboard,
    get_product_list_for_editing_keyboard,
)
from src.shopim.services.product_management_service import ProductManagementService
from src.shopim.services.warehouse_service import WarehouseService
from src.shopim.states.admin import ProductEditingState


from src.shopim.filters import IsAdminFilter


router = Router(name="admin-product-editing-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

ITEMS_PER_PAGE = 5


async def _show_product_edit_menu(
    target: types.Message | types.CallbackQuery,
    product_id: int,
    page: int,
    session: AsyncSession,
    success_message: str | None = None,
):
    product = await session.get(Product, product_id)
    if not product:
        await target.answer("Mahsulot topilmadi.")
        return

    text = (
        f"Mahsulotni tahrirlash: <b>{product.name}</b>\n\n"
        f"Qaysi maydonni o'zgartirmoqchisiz?"
    )
    if success_message:
        text = f"✅ {success_message}\n\n{text}"

    keyboard = get_product_edit_menu_keyboard(product, page)

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def _show_products_for_editing(
    target: types.Message | types.CallbackQuery, page: int, session: AsyncSession
):
    service = WarehouseService(session, items_per_page=ITEMS_PER_PAGE)
    result = await service.get_products_stock(page=page)

    text = "Tahrirlash uchun mahsulot tanlang:"
    keyboard = get_product_list_for_editing_keyboard(
        products=result.products,
        total_pages=result.total_pages,
        current_page=result.current_page,
    )

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard)
    else:
        await target.answer(text, reply_markup=keyboard)


@router.message(F.text == "✏️ Tovarlarni boshqarish")
async def start_editing_handler(message: types.Message, session: AsyncSession):
    await _show_products_for_editing(message, 1, session)


@router.callback_query(ProductEditCallback.filter(F.action == "page"))
async def paginate_products_to_edit_handler(
    callback: types.CallbackQuery,
    callback_data: ProductEditCallback,
    session: AsyncSession,
):
    await _show_products_for_editing(callback, callback_data.page, session)
    await callback.answer()


@router.callback_query(ProductEditCallback.filter(F.action == "select"))
async def select_product_to_edit_handler(
    callback: types.CallbackQuery,
    callback_data: ProductEditCallback,
    state: FSMContext,
    session: AsyncSession,
):
    await state.set_state(ProductEditingState.choosing_field)
    await state.update_data(
        product_id=callback_data.product_id, page=callback_data.page
    )
    await _show_product_edit_menu(
        callback, callback_data.product_id, callback_data.page, session
    )
    await callback.answer()


@router.callback_query(
    ProductEditFieldCallback.filter(F.action == "back_to_menu"),
    ProductEditingState.getting_name,
    ProductEditingState.getting_description,
    ProductEditingState.getting_image,
    ProductEditingState.getting_cost_price,
    ProductEditingState.getting_sale_price,
    ProductEditingState.getting_low_stock_threshold,
)
async def back_to_edit_menu_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(ProductEditingState.choosing_field)
    data = await state.get_data()
    await _show_product_edit_menu(
        callback, data["product_id"], data["page"], session
    )
    await callback.answer()


@router.callback_query(
    ProductEditFieldCallback.filter(F.action == "choose_field"),
    ProductEditingState.choosing_field,
)
async def choose_field_to_edit_handler(
    callback: types.CallbackQuery,
    callback_data: ProductEditFieldCallback,
    state: FSMContext,
):
    field_map = {
        "name": (ProductEditingState.getting_name, "Yangi nomni kiriting:"),
        "description": (
            ProductEditingState.getting_description,
            "Yangi tavsifni kiriting:",
        ),
        "image": (ProductEditingState.getting_image, "Yangi rasmni yuboring:"),
        "sale_price_per_gram": (
            ProductEditingState.getting_sale_price,
            "Yangi sotuv narxini kiriting (so'm/gramm):",
        ),
        "cost_price_per_gram": (
            ProductEditingState.getting_cost_price,
            "Yangi tannarxni kiriting (so'm/gramm):",
        ),
        "low_stock_threshold_grams": (
            ProductEditingState.getting_low_stock_threshold,
            "Yangi minimal qoldiq chegarasini kiriting (gramm):",
        ),
    }
    field = callback_data.field
    if field in field_map:
        new_state, prompt = field_map[field]
        await state.set_state(new_state)
        await callback.message.edit_text(prompt, reply_markup=get_back_to_edit_menu_keyboard())
    await callback.answer()


@router.callback_query(
    ProductEditFieldCallback.filter(F.action == "toggle_active"),
    ProductEditingState.choosing_field,
)
async def toggle_product_active_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    product_id = data["product_id"]
    page = data["page"]

    service = ProductManagementService(session)
    product = await session.get(Product, product_id)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return

    new_status = not product.is_active
    await service.update_product(product_id, {"is_active": new_status})

    success_message = "Mahsulot yashirildi" if not new_status else "Mahsulot ko'rsatildi"

    await _show_product_edit_menu(
        callback, product_id, page, session, success_message=success_message
    )
    await callback.answer(success_message)


@router.callback_query(
    ProductEditFieldCallback.filter(F.action == "delete_start"),
    ProductEditingState.choosing_field,
)
async def start_delete_product_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    product_id = data["product_id"]

    service = ProductManagementService(session)
    can_delete = await service.can_delete_product(product_id)

    if not can_delete:
        await callback.answer(
            "Bu mahsulotni o'chirib bo'lmaydi, chunki u bilan bog'liq buyurtmalar mavjud. "
            "O'chirish o'rniga yashirishingiz mumkin.",
            show_alert=True,
        )
        return

    product = await session.get(Product, product_id)
    text = (
        f"❓ Rostdan ham <b>{product.name}</b> mahsulotini o'chirmoqchimisiz?\n\n"
        "<b>DIQQAT:</b> Bu amalni orqaga qaytarib bo'lmaydi!"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_product_delete_confirmation_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


async def _process_update(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
    field_name: str,
    value: any,
    success_message: str,
):
    data = await state.get_data()
    product_id = data["product_id"]
    page = data["page"]

    service = ProductManagementService(session)
    await service.update_product(product_id, {field_name: value})

    await state.set_state(ProductEditingState.choosing_field)
    await _show_product_edit_menu(
        message, product_id, page, session, success_message=success_message
    )


@router.callback_query(
    ProductEditFieldCallback.filter(F.action == "delete_confirm"),
    ProductEditingState.choosing_field,
)
async def confirm_delete_product_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    product_id = data["product_id"]
    page = data["page"]

    service = ProductManagementService(session)
    deleted = await service.delete_product(product_id)

    await state.clear()
    await callback.answer("Mahsulot o'chirildi.", show_alert=True)

    if deleted:
        await _show_products_for_editing(callback, page, session)
    else:
        await callback.message.edit_text(
            "❌ Mahsulotni o'chirishda xatolik yuz berdi. "
            "Balki u buyurtmalar bilan bog'liqdir."
        )

@router.message(ProductEditingState.getting_name)
async def process_new_name_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await _process_update(message, state, session, "name", message.text, "Nom yangilandi")


@router.message(ProductEditingState.getting_description)
async def process_new_description_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await _process_update(message, state, session, "description", message.text, "Tavsif yangilandi")


@router.message(ProductEditingState.getting_image, F.photo)
async def process_new_image_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await _process_update(message, state, session, "image_file_id", message.photo[-1].file_id, "Rasm yangilandi")


async def _process_decimal_update(
    message: types.Message, state: FSMContext, session: AsyncSession, field_name: str, success_message: str
):
    try:
        value = Decimal(message.text.replace(",", "."))
        if value < 0:
            raise ValueError
        await _process_update(message, state, session, field_name, str(value), success_message)
    except (InvalidOperation, ValueError):
        await message.answer("Xato. Iltimos, musbat raqam kiriting.")


@router.message(ProductEditingState.getting_sale_price)
async def process_new_sale_price_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await _process_decimal_update(message, state, session, "sale_price_per_gram", "Sotuv narxi yangilandi")


@router.message(ProductEditingState.getting_cost_price)
async def process_new_cost_price_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await _process_decimal_update(message, state, session, "cost_price_per_gram", "Tannarx yangilandi")


@router.message(ProductEditingState.getting_low_stock_threshold)
async def process_new_low_stock_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await _process_decimal_update(message, state, session, "low_stock_threshold_grams", "Minimal qoldiq chegarasi yangilandi")