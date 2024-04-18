import os
from typing import Union

from aiogram import Bot, types
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.loyality import loyality_crud
from app.crud.payment import payments_crud
from app.schemas.loyality import LoyalityPayment
from app.schemas.payment import (
    PaymentUpdateGeneratedPaymentId,
    PaymentUpdateIsPaid,
)
from app.services.yookassa_payment import (
    check_payment,
    create_payment,
)

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

PAYMENT_WAS_CREATED = (
    'По Вашему заказу сформирован платежный документ № {}.\n'
    'Для оплаты перейдите по <a href="{}">ссылке</a> '
    'или нажмите на кнопку:'
)
PAYMENT_TIME_EXPIRED = (
    'Платеж № {} не был выполнен. Истекло время ожидания оплаты.'
)

ONLINE_PAYMENT_ADMIN_CONFIRMATION = (
    'Оплата по счету № {} на сумму {} {} прошла успешно.'
    '\nКлиенту {} баллов: {}.'
)
ONLINE_PAYMENT_CLIENT_CONFIRMATION = (
    'Оплата по счету № {} на сумму {} {} прошла успешно.\n{} баллов: {}.'
    '\nБлагодарим Вам за визит!'
)

CASH_PAYMENT_ADMIN_CONFIRMATION = (
    'Оплата на сумму {} RUB прошла успешно.\nКлиенту {} баллов: {}.'
)
CASH_PAYMENT_CLIENT_CONFIRMATION = (
    'Оплата на сумму {} RUB прошла успешно.\n{} баллов: {}.'
    '\nБлагодарим Вам за визит!'
)

LOYALITY_ACTION_ADMIN_CONFIRMATION = (
    'Клиенту с номером телефона {} {} баллов: {}.'
)
LOYALITY_ACTION_CLIENT_CONFIRMATION = 'Вам {} баллов: {}.'


async def update_payment(
    update_data: Union[PaymentUpdateIsPaid, PaymentUpdateGeneratedPaymentId],
    payment_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await payments_crud.update(
        await payments_crud.get(payment_id, session),
        update_data,
        session,
    )


"""BACKGROUND TASKS FOR PAYMENT"""


async def payment_background_tasks(
    admin_telegram_id,
    payment,
    payer_telegram_id,
    admin_id,
    payer_id,
    loyality_action,
    loyality_amount,
    session,
):
    yookassa_payment_id, yookassa_payment_url = await create_payment(
        payment, payer_telegram_id
    )
    await update_payment(
        PaymentUpdateGeneratedPaymentId(
            generated_payment_id=yookassa_payment_id
        ),
        payment.id,
        session,
    )
    await send_payment_message(
        admin_telegram_id,
        payer_telegram_id,
        payment.id,
        yookassa_payment_id,
        yookassa_payment_url,
        admin_id,
        payer_id,
        loyality_action,
        loyality_amount,
        session,
    )


async def send_payment_message(
    admin_telegram_id,
    payer_telegram_id,
    db_payment_id,
    yookassa_payment_id,
    yookassa_payment_url,
    admin_id,
    payer_id,
    loyality_action,
    loyality_amount,
    session,
):
    await bot.send_message(
        payer_telegram_id,
        text=PAYMENT_WAS_CREATED.format(
            yookassa_payment_id, yookassa_payment_url
        ),
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text='ОПЛАТИТЬ',
                        web_app=types.WebAppInfo(url=yookassa_payment_url),
                    )
                ]
            ]
        ),
    )
    is_paid, payment = await check_payment(yookassa_payment_id)
    if is_paid:
        await update_payment(
            PaymentUpdateIsPaid(is_paid=True),
            db_payment_id,
            session,
        )
        await loyality_crud.create(
            admin_id,
            payer_id,
            LoyalityPayment(
                action=loyality_action,
                amount=loyality_amount,
                user_id=payer_id,
                payment_id=db_payment_id,
            ),
            session,
        )
        return await send_successful_online_payment_message(
            admin_telegram_id,
            payer_telegram_id,
            payment,
            loyality_action,
            loyality_amount,
        )
    return await send_failed_payment_message(
        [admin_telegram_id, payer_telegram_id], payment
    )


async def send_successful_online_payment_message(
    admin_telegram_id,
    payer_telegram_id,
    payment,
    loyality_action,
    loyality_amount,
):
    await bot.send_message(
        admin_telegram_id,
        text=ONLINE_PAYMENT_ADMIN_CONFIRMATION.format(
            payment.id,
            payment.amount.value,
            payment.amount.currency,
            loyality_action,
            abs(loyality_amount),
        ),
    )
    await bot.send_message(
        payer_telegram_id,
        text=ONLINE_PAYMENT_CLIENT_CONFIRMATION.format(
            payment.id,
            payment.amount.value,
            payment.amount.currency,
            loyality_action.capitalize(),
            abs(loyality_amount),
        ),
    )


async def send_successful_cash_payment_message(
    admin_telegram_id,
    payer_telegram_id,
    price,
    loyality_action,
    loyality_amount,
):
    await bot.send_message(
        admin_telegram_id,
        text=CASH_PAYMENT_ADMIN_CONFIRMATION.format(
            price,
            loyality_action,
            abs(loyality_amount),
        ),
    )
    await bot.send_message(
        payer_telegram_id,
        text=CASH_PAYMENT_CLIENT_CONFIRMATION.format(
            price,
            loyality_action.capitalize(),
            abs(loyality_amount),
        ),
    )


async def send_failed_payment_message(telegram_id_list, payment):
    for telegram_id in telegram_id_list:
        await bot.send_message(
            telegram_id, text=PAYMENT_TIME_EXPIRED.format(payment.id)
        )


async def send_successful_loyality_action(
    admin_telegram_id, user_telegram_id, phone_number, action, amount
):
    await bot.send_message(
        admin_telegram_id,
        text=LOYALITY_ACTION_ADMIN_CONFIRMATION.format(
            phone_number,
            action,
            abs(amount),
        ),
    )
    await bot.send_message(
        user_telegram_id,
        text=LOYALITY_ACTION_CLIENT_CONFIRMATION.format(
            action,
            abs(amount),
        ),
    )
