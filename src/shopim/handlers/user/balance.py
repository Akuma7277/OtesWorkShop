from typing import Optional

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopim.db.models import BalanceTxType, User, UserStatus
from src.shopim.keyboards.inline.balance import (
    BalanceHistoryPageCallback,
    get_balance_history_keyboard,
)
from src.shopim.services.balance_service import BalanceService


from src.shopim.filters import IsApprovedUserFilter


router = Router(name="balance-router")
router.message.filter(IsApprovedUserFilter())
router.callback_query.filter(IsApprovedUserFilter())

ITEMS_PER_PAGE = 10

TX_TYPE_MAP = {
    BalanceTxType.TOPUP: "📥 Balans to'ldirish",
    BalanceTxType.PURCHASE: "📤 Xarid",
    BalanceTxType.REFUND: "📥 Pul qaytarilishi",
    BalanceTxType.MANUAL_CREDIT: "📥 Manual to'ldirish",
    BalanceTxType.MANUAL_DEBIT: "📤 Manual yechish",
}


def format_transaction_history(transactions) -> str:
    if not transactions:
        return "Tranzaksiyalar tarixi bo'sh."

    lines = []
    for tx in transactions:
        sign = "+" if tx.amount > 0 else ""
        tx_type_str = TX_TYPE_MAP.get(tx.type, "Noma'lum operatsiya")
        lines.append(
            f"{tx.created_at.strftime('%d.%m.%Y %H:%M')} | {tx_type_str}: <b>{sign}{tx.amount:.2f} so'm</b>"
        )
    return "\n".join(lines)


async def show_balance_and_history(
    target: types.Message | types.CallbackQuery, user: User, page: int, session: AsyncSession
):
    service = BalanceService(session, items_per_page=ITEMS_PER_PAGE)
    result = await service.get_balance_and_history(user_id=user.id, page=page)

    history_text = format_transaction_history(result.transactions)
    page_info = (
        f"(Sahifa {result.current_page}/{result.total_pages})"
        if result.total_pages > 0
        else ""
    )

    text = (
        f"💰 <b>Balansingiz: {result.current_balance:.2f} so'm</b>\n\n"
        f"📜 <b>Tranzaksiyalar tarixi</b> {page_info}\n"
        f"------------------------------------\n"
        f"{history_text}"
    )

    keyboard = get_balance_history_keyboard(
        total_pages=result.total_pages, current_page=result.current_page
    )

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "💰 Balansim")
async def show_balance_handler(message: types.Message, user: User, session: AsyncSession):
    await show_balance_and_history(message, user, 1, session)


@router.callback_query(BalanceHistoryPageCallback.filter())
async def paginate_balance_history_handler(
    callback: types.CallbackQuery,
    callback_data: BalanceHistoryPageCallback,
    user: User,
    session: AsyncSession,
):
    await show_balance_and_history(callback, user, callback_data.page, session)
    await callback.answer()