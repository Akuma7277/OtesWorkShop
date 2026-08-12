from decimal import Decimal, InvalidOperation
from typing import Optional

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.settings_models import BotSettings
from src.shopim.db.models import Admin, AdminRole
from src.shopim.keyboards.inline.admin.settings_management import (
    SettingsCallback,
    get_back_to_settings_menu_keyboard,
    get_settings_menu_keyboard,
)
from src.shopim.services.settings_service import SettingsService
from src.shopim.states.admin import SettingsManagementState


from src.shopim.filters import IsSuperAdminFilter


router = Router(name="admin-settings-management-router")
router.message.filter(IsSuperAdminFilter())
router.callback_query.filter(IsSuperAdminFilter())


async def _show_settings_menu(
    target: types.Message | types.CallbackQuery,
    session: AsyncSession,
    success_message: str | None = None,
):
    service = SettingsService(session)
    settings = await service.get_bot_settings()

    settings_text = "\n".join(
        [
            f"  - {field.description or name}: <b>{getattr(settings, name)}</b>"
            for name, field in BotSettings.model_fields.items()
        ]
    )

    text = _("<b>⚙️ Joriy sozlamalar</b>\n\n{settings_text}\n\nO'zgartirish uchun maydonni tanlang:").format(settings_text=settings_text)
    if success_message:
        text = _("✅ {success_message}\n\n{text}").format(success_message=success_message, text=text)

    keyboard = get_settings_menu_keyboard()

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")  # type: ignore


@router.message(F.text == "⚙️ Sozlamalar")
async def settings_menu_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.set_state(SettingsManagementState.choosing_setting)
    await _show_settings_menu(message, session)


@router.callback_query(
    SettingsCallback.filter(F.action == "back_to_menu"),
    SettingsManagementState.getting_new_value,
)
async def back_to_settings_menu_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(SettingsManagementState.choosing_setting)
    await _show_settings_menu(callback, session)
    await callback.answer()


@router.callback_query(
    SettingsCallback.filter(F.action == "choose_field"),
    SettingsManagementState.choosing_setting,
)
async def choose_setting_to_edit_handler(
    callback: types.CallbackQuery, callback_data: SettingsCallback, state: FSMContext
):
    field_name = callback_data.field
    field_info = BotSettings.model_fields.get(field_name)
    if not field_info:
        await callback.answer("Noma'lum sozlama.", show_alert=True)
        return  # type: ignore

    await state.set_state(SettingsManagementState.getting_new_value)
    await state.update_data(field_to_edit=field_name)

    prompt = _("Iltimos, '{field_description}' uchun yangi qiymatni kiriting:").format(field_description=field_info.description or field_name)
    await callback.message.edit_text(prompt, reply_markup=get_back_to_settings_menu_keyboard())
    await callback.answer()


@router.message(SettingsManagementState.getting_new_value)
async def get_new_setting_value_handler(
    message: types.Message, state: FSMContext, session: AsyncSession, admin: Admin
):
    data = await state.get_data()
    field_name = data.get("field_to_edit")
    new_value_str = message.text

    if not field_name:
        await state.clear()  # type: ignore
        await message.answer(_("Xatolik yuz berdi. Iltimos, boshidan boshlang."))  # type: ignore
        return

    service = SettingsService(session)
    
    try:
        # Let the service handle validation and update
        await service.update_bot_settings({field_name: new_value_str}, admin_id=admin.id)  # type: ignore
        await state.set_state(SettingsManagementState.choosing_setting)
        field_info = BotSettings.model_fields[field_name]
        await _show_settings_menu(
            message, session, success_message=_("'{field_description}' yangilandi").format(field_description=field_info.description or field_name)
        )
    except (ValidationError, ValueError) as e:
        await message.answer(_("Xato: Noto'g'ri format.\nIltimos, qiymatni to'g'ri kiriting.\n\n_{error_message}_").format(error_message=e))  # type: ignore
    except Exception as e:  # type: ignore
        await message.answer(_("Sozlamani yangilashda noma'lum xatolik yuz berdi: {error_message}").format(error_message=e))  # type: ignore