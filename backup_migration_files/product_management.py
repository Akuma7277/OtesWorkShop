import math
from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import Admin
from src.shopim.db.repositories.category_repository import CategoryRepository
from src.shopim.keyboards.inline.admin.product_management import (
    ProductCategoryCallback,
    ProductCreationCallback,
    get_cancellation_keyboard,
    get_category_selection_keyboard,
    get_skip_or_cancel_keyboard,
)
from src.shopim.services.product_management_service import ProductManagementService
from src.shopim.states.admin import ProductCreationState

CATEGORIES_PER_PAGE = 6


class IsAdminFilter:
    def __call__(self, admin: Optional[Admin]) -> bool:
        return admin is not None


router = Router(name="admin-product-management-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


# --- Cancellation Handler ---
@router.callback_query(ProductCreationCallback.filter(F.action == "cancel"))
async def cancel_creation_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Mahsulot yaratish bekor qilindi.")
    await callback.answer()


# --- Product Creation Flow ---
@router.message(F.text == "➕ Tovar qo'shish")
async def start_product_creation_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(ProductCreationState.getting_name)
    await message.answer(
        "Yangi mahsulot yaratish boshlandi.\n\n"
        "Iltimos, mahsulot nomini kiriting:",
        reply_markup=get_cancellation_keyboard(),
    )


@router.message(ProductCreationState.getting_name)
async def get_name_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    if not message.text or len(message.text) < 3:
        await message.answer("Mahsulot nomi kamida 3 belgidan iborat bo'lishi kerak.")
        return

    await state.update_data(name=message.text)
    await state.set_state(ProductCreationState.getting_category)

    repo = CategoryRepository(session)
    total_cats = await repo.count_all_active()
    if total_cats == 0:
        await state.clear()
        await message.answer(
            "Xatolik: Tizimda faol kategoriyalar mavjud emas. "
            "Avval kategoriya qo'shing."
        )
        return

    total_pages = math.ceil(total_cats / CATEGORIES_PER_PAGE)
    cats = await repo.get_all_active_paginated(offset=0, limit=CATEGORIES_PER_PAGE)

    await message.answer(
        "Endi mahsulot kategoriyasini tanlang:",
        reply_markup=get_category_selection_keyboard(
            categories=cats, total_pages=total_pages, current_page=1
        ),
    )


@router.callback_query(ProductCategoryCallback.filter(F.action == "page"))
async def paginate_category_handler(
    callback: types.CallbackQuery,
    callback_data: ProductCategoryCallback,
    session: AsyncSession,
):
    repo = CategoryRepository(session)
    total_cats = await repo.count_all_active()
    total_pages = math.ceil(total_cats / CATEGORIES_PER_PAGE)
    offset = (callback_data.page - 1) * CATEGORIES_PER_PAGE
    cats = await repo.get_all_active_paginated(offset=offset, limit=CATEGORIES_PER_PAGE)

    await callback.message.edit_reply_markup(
        reply_markup=get_category_selection_keyboard(
            categories=cats, total_pages=total_pages, current_page=callback_data.page
        )
    )
    await callback.answer()


@router.callback_query(ProductCategoryCallback.filter(F.action == "select"))
async def get_category_handler(
    callback: types.CallbackQuery,
    callback_data: ProductCategoryCallback,
    state: FSMContext,
):
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(ProductCreationState.getting_description)
    await callback.message.edit_text(
        "Kategoriya tanlandi. Endi mahsulot uchun batafsil tavsif kiriting.",
        reply_markup=get_skip_or_cancel_keyboard("skip_description"),
    )


@router.callback_query(ProductCreationCallback.filter(F.action == "skip_description"))
async def skip_description_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    await state.set_state(ProductCreationState.getting_image)
    await callback.message.edit_text(
        "Tavsif o'tkazib yuborildi. Endi mahsulot rasmini yuboring.",
        reply_markup=get_skip_or_cancel_keyboard("skip_image"),
    )


@router.message(ProductCreationState.getting_description)
async def get_description_handler(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ProductCreationState.getting_image)
    await message.answer(
        "Tavsif qabul qilindi. Endi mahsulot rasmini yuboring.",
        reply_markup=get_skip_or_cancel_keyboard("skip_image"),
    )


@router.callback_query(ProductCreationCallback.filter(F.action == "skip_image"))
async def skip_image_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(image_file_id=None)
    await state.set_state(ProductCreationState.getting_cost_price)
    await callback.message.edit_text(
        "Rasm o'tkazib yuborildi. Endi mahsulotning 1 gramm uchun tannarxini kiriting (so'mda).",
        reply_markup=get_cancellation_keyboard(),
    )


@router.message(ProductCreationState.getting_image, F.photo)
async def get_image_handler(message: types.Message, state: FSMContext):
    await state.update_data(image_file_id=message.photo[-1].file_id)
    await state.set_state(ProductCreationState.getting_cost_price)
    await message.answer(
        "Rasm qabul qilindi. Endi mahsulotning 1 gramm uchun tannarxini kiriting (so'mda).",
        reply_markup=get_cancellation_keyboard(),
    )


@router.message(ProductCreationState.getting_image)
async def wrong_image_handler(message: types.Message):
    await message.answer(
        "Iltimos, rasm yuboring yoki bu qadamni o'tkazib yuboring.",
        reply_markup=get_skip_or_cancel_keyboard("skip_image"),
    )


async def _parse_decimal(text: str) -> Decimal | None:
    try:
        price = Decimal(text.replace(",", "."))
        if price < 0:
            return None
        return price
    except (InvalidOperation, ValueError):
        return None


@router.message(ProductCreationState.getting_cost_price)
async def get_cost_price_handler(message: types.Message, state: FSMContext):
    cost_price = await _parse_decimal(message.text)
    if cost_price is None:
        await message.answer("Xato. Tannarxni musbat raqamda kiriting (masalan, 15000.50).")
        return

    await state.update_data(cost_price=str(cost_price))
    await state.set_state(ProductCreationState.getting_sale_price)
    await message.answer(
        "Tannarx qabul qilindi. Endi 1 gramm uchun sotuv narxini kiriting (so'mda).",
        reply_markup=get_cancellation_keyboard(),
    )


@router.message(ProductCreationState.getting_sale_price)
async def get_sale_price_handler(message: types.Message, state: FSMContext):
    sale_price = await _parse_decimal(message.text)
    if sale_price is None:
        await message.answer("Xato. Sotuv narxini musbat raqamda kiriting (masalan, 20000).")
        return

    await state.update_data(sale_price=str(sale_price))
    await state.set_state(ProductCreationState.getting_initial_stock)
    await message.answer(
        "Sotuv narxi qabul qilindi. Endi boshlang'ich qoldiqni grammda kiriting (masalan, 1000).",
        reply_markup=get_cancellation_keyboard(),
    )


@router.message(ProductCreationState.getting_initial_stock)
async def get_initial_stock_handler(message: types.Message, state: FSMContext):
    initial_stock = await _parse_decimal(message.text)
    if initial_stock is None:
        await message.answer("Xato. Boshlang'ich qoldiqni musbat raqamda kiriting (masalan, 1000).")
        return

    await state.update_data(initial_stock=str(initial_stock))
    await state.set_state(ProductCreationState.getting_low_stock_threshold)
    await message.answer(
        "Boshlang'ich qoldiq qabul qilindi. Endi 'low stock' ogohlantirishi uchun minimal miqdorni kiriting (grammda).",
        reply_markup=get_cancellation_keyboard(),
    )


@router.message(ProductCreationState.getting_low_stock_threshold)
async def get_low_stock_threshold_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, admin: Admin
):
    low_stock_threshold = await _parse_decimal(message.text)
    if low_stock_threshold is None:
        await message.answer("Xato. Minimal miqdorni musbat raqamda kiriting (masalan, 100).")
        return

    product_data = await state.get_data()
    product_data["low_stock_threshold"] = str(low_stock_threshold)
    await state.clear()

    try:
        service = ProductManagementService(session)
        new_product = await service.create_product(product_data, admin_id=admin.id)
        await message.answer(
            f"✅ Mahsulot muvaffaqiyatli yaratildi!\n\n"
            f"Nomi: <b>{new_product.name}</b>\n"
            f"ID: {new_product.id}\n"
            f"Sotuv narxi: {new_product.sale_price_per_gram} so'm/gr\n"
            f"Qoldiq: {new_product.stock_grams} gr",
            parse_mode="HTML",
        )
    except Exception as e:
        # Log error `e`
        await message.answer(f"❌ Mahsulot yaratishda xatolik yuz berdi: {e}")