from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.core.config import get_settings
from src.shopim.db.models import User
from src.shopim.states.registration import RegistrationStates
from src.shopim.keyboards.inline.registration import get_accept_rules_keyboard
from src.shopim.keyboards.inline.language import (
    get_language_selection_keyboard,
    LanguageCallback,
)
from src.shopim.keyboards.reply.registration import get_contact_keyboard
from src.shopim.services.registration_service import RegistrationService
from src.shopim.services.notification_service import NotificationService

router = Router(name="registration-router")

@router.message(CommandStart())
async def start_handler(
    message: types.Message, state: FSMContext, user: User | None
):
    if user:
        # This case is for PENDING, REJECTED, BLOCKED users.
        # Approved users are handled by the main_menu router.
        await message.answer(
            _("Siz avval ro'yxatdan o'tgansiz. Iltimos, admin tasdig'ini kuting.")
        )
        return

    # New user
    await state.clear()
    await state.set_state(RegistrationStates.choosing_language)
    await message.answer(
        _("Tilni tanlang / Выберите язык:"),
        reply_markup=get_language_selection_keyboard(),
    )


@router.callback_query(
    StateFilter(RegistrationStates.choosing_language), LanguageCallback.filter()
)
async def choose_language_handler(
    callback: types.CallbackQuery, callback_data: LanguageCallback, state: FSMContext
):
    lang_code = callback_data.code
    await state.update_data(language_code=lang_code)
    text = _("Assalomu alaykum! Shopim botiga xush kelibsiz.\nRo'yxatdan o'tish uchun ism-familiyangizni kiriting:")

    await state.set_state(RegistrationStates.getting_full_name)
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(RegistrationStates.getting_full_name)
async def get_name_handler(message: types.Message, state: FSMContext):
    if not message.text or len(message.text.split()) < 2:
        await message.answer(
            _("Iltimos, to'liq ism-familiyangizni kiriting (masalan, Alisher Valiyev).")
        )
        return
    await state.update_data(full_name=message.text)
    await state.set_state(RegistrationStates.getting_phone_number)
    await message.answer(
        _("Ajoyib! Endi telefon raqamingizni yuboring."),
        reply_markup=get_contact_keyboard(),
    )


@router.message(RegistrationStates.getting_phone_number, F.contact)
async def get_contact_handler(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone=phone_number)
    await state.set_state(RegistrationStates.getting_address)
    await message.answer(
        _("Raqamingiz qabul qilindi. Endi yashash manzilingizni to'liq kiriting:"),
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(RegistrationStates.getting_address)
async def get_address_handler(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) < 10:
        await message.answer(_("Iltimos, manzilingizni to'liqroq kiriting."))
        return
    await state.update_data(address=message.text)
    await state.set_state(RegistrationStates.getting_age)
    await message.answer(_("Manzilingiz qabul qilindi. Endi yoshingizni kiriting:"))


@router.message(RegistrationStates.getting_age)
async def get_age_handler(message: types.Message, state: FSMContext):
    settings = get_settings()
    try:
        age = int(message.text)
        if not (settings.min_user_age <= age <= settings.max_user_age):
            raise ValueError
    except (ValueError, TypeError):
        await message.answer(
            _("Iltimos, yoshingizni to'g'ri kiriting (raqamda, {min_age} dan {max_age} gacha).").format(
                min_age=settings.min_user_age, max_age=settings.max_user_age
            )
        )
        return

    await state.update_data(age=age)
    await state.set_state(RegistrationStates.accepting_rules)
    # This should be a more detailed text with rules
    await message.answer(
        _(
            "Ro'yxatdan o'tish deyarli yakunlandi.\n"
            "Iltimos, botdan foydalanish qoidalari bilan tanishib chiqing va roziligingizni bildiring."
        ),
        reply_markup=get_accept_rules_keyboard()
    )

@router.callback_query(F.data == "register_cancel")
async def cancel_registration_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(_("Ro'yxatdan o'tish bekor qilindi."))
    await callback.answer()

@router.callback_query(RegistrationStates.accepting_rules, F.data == "register_accept_rules")
async def accept_rules_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    user_data = await state.get_data()
    
    reg_service = RegistrationService(session)
    
    try:
        new_user = await reg_service.create_pending_user(
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=user_data["full_name"],
            phone=user_data["phone"],
            address=user_data["address"],
            age=user_data["age"],
            language_code=user_data["language_code"],
        )
        
        await state.clear()
        
        await callback.message.edit_text(
            _(
                "Tabriklaymiz, {full_name}! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
                "Sizning profilingiz tasdiqlash uchun adminga yuborildi. "
                "Tasdiqlangandan so'ng sizga xabar beramiz."
            ).format(full_name=new_user.full_name)
        )
        
        # Notify all admins about the new user
        notification_service = NotificationService(bot, session)
        await notification_service.notify_admins_of_new_user(new_user)
        
    except Exception as e:
        # In a real app, log this error properly
        print(f"Error during user creation: {e}")
        await callback.message.edit_text(_("Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."))
    
    finally:
        await callback.answer()
