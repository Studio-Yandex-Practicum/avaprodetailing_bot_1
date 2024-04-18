from sqlalchemy.ext.asyncio.session import AsyncSession

from app.crud.loyality import loyality_crud
from app.schemas.loyality import LoyalityPayment
from app.services.utils import (
    send_successful_cash_payment_message,
    send_successful_loyality_action,
)


async def cash_payment_background_tasks(
    admin_telegram_id,
    admin_id,
    user_telegram_id,
    user_id,
    action,
    amount,
    payment_id,
    price,
    session: AsyncSession,
):
    await loyality_crud.create(
        admin_id,
        user_id,
        LoyalityPayment(
            action=action,
            amount=amount,
            user_id=user_id,
            payment_id=payment_id,
        ),
        session,
    )
    await send_successful_cash_payment_message(
        admin_telegram_id, user_telegram_id, price, action, amount
    )


async def loyality_background_tasks(
    admin_telegram_id,
    user_telegram_id,
    user_phone_number,
    action,
    amount,
):
    await send_successful_loyality_action(
        admin_telegram_id, user_telegram_id, user_phone_number, action, amount
    )
