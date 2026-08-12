from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.settings_models import BotSettings
from src.shopim.db.models import Admin
from src.shopim.filters import IsAdminFilter
from src.shopim.keyboards.inline.admin.settings_management import (
    SettingsCallback,
    get_back_to_settings_menu_keyboard,
    get_settings_menu_keyboard,
)
from src.shopim.keyboards.reply.admin import get_admin_main_keyboard
from src.shopim.services.settings_service import SettingsService
from src.shopim.states.admin import SettingsManagementState

router = Router(name="admin-settings-management-router")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


async def _show_settings_menu(
    target: types.Message | types.CallbackQuery,
    session: AsyncSession,
    success_message: str | None = None,
):
    service = SettingsService(session)
    settings = await service.get_bot_settings()

    settings_text = "\n".join(
        [
            f"• <b>{field.description or name}</b>: <code>{getattr(settings, name)}</code>"
            for name, field in BotSettings.model_fields.items()
        ]
    )

    text = f"<b>⚙️ Tizim va Baza Sozlamalari</b>\n\n{settings_text}\n\n<i>O'zgartirmoqchi bo'lgan parametrni tanlang:</i>"
    if success_message:
        text = f"✅ <b>{success_message}</b>\n\n{text}"

    keyboard = get_settings_menu_keyboard()

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text.in_({"⚙️ Sozlamalar", "⚙️ Настройки", "Sozlamalar", "Настройки"}), StateFilter("*"))
async def settings_menu_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.set_state(SettingsManagementState.choosing_setting)
    await _show_settings_menu(message, session)


@router.callback_query(SettingsCallback.filter(F.action == "toggle_admin_lang"))
async def toggle_admin_lang_handler(
    callback: types.CallbackQuery, admin: Admin, session: AsyncSession
):
    new_lang = "ru" if admin.language_code == "uz" else "uz"
    admin.language_code = new_lang
    await session.commit()

    alert_text = (
        "Admin tili O'zbekchaga o'zgartirildi!"
        if new_lang == "uz"
        else "Язык админки изменен на Русский!"
    )
    await callback.answer(alert_text, show_alert=True)
    await callback.message.answer(
        "Admin Paneli:" if new_lang == "uz" else "Панель администратора:",
        reply_markup=get_admin_main_keyboard(),
    )


@router.callback_query(SettingsCallback.filter(F.action == "back_to_menu"), StateFilter("*"))
async def back_to_settings_menu_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(SettingsManagementState.choosing_setting)
    await _show_settings_menu(callback, session)
    await callback.answer()


@router.callback_query(SettingsCallback.filter(F.action == "choose_field"), StateFilter("*"))
async def choose_setting_to_edit_handler(
    callback: types.CallbackQuery, callback_data: SettingsCallback, state: FSMContext
):
    field_name = callback_data.field
    field_info = BotSettings.model_fields.get(field_name)
    if not field_info:
        await callback.answer("Noma'lum sozlama.", show_alert=True)
        return

    await state.set_state(SettingsManagementState.getting_new_value)
    await state.update_data(field_to_edit=field_name)

    field_desc = field_info.description or field_name
    prompt = f"✍️ Iltimos, <b>{field_desc}</b> uchun yangi qiymatni kiriting:"
    await callback.message.edit_text(prompt, reply_markup=get_back_to_settings_menu_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message(SettingsManagementState.getting_new_value)
async def get_new_setting_value_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, admin: Admin
):
    data = await state.get_data()
    field_name = data.get("field_to_edit")
    new_value_str = message.text

    if not field_name:
        await state.clear()
        await message.answer("Xatolik yuz berdi. Iltimos, boshidan boshlang.")
        return

    service = SettingsService(session)

    try:
        await service.update_bot_settings({field_name: new_value_str}, admin_id=admin.id)
        await state.set_state(SettingsManagementState.choosing_setting)
        field_info = BotSettings.model_fields[field_name]
        field_desc = field_info.description or field_name
        await _show_settings_menu(
            message, session, success_message=f"'{field_desc}' muvaffaqiyatli yangilandi!"
        )
    except (ValidationError, ValueError) as e:
        await message.answer(f"❌ Xato: Noto'g'ri format.\nIltimos, qiymatni to'g'ri kiriting.\n\n<i>{e}</i>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Sozlamani yangilashda xatolik: {e}")