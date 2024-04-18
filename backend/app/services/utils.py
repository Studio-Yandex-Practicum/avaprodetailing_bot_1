import os
from typing import Union

from aiogram import Bot, types
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.db import get_async_session
from app.crud.payment import payments_crud
from app.schemas.payment import (
    PaymentUpdateGeneratedPaymentId,
    PaymentUpdateIsPaid,
)
from app.services.yookassa_payment import (
    create_payment,
    check_payment,
)

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

PAYMENT_TIME_EXPIRED = (
    'Платеж № {} не был выполнен. Истекло время ожидания оплаты.'
)
PAYMENT_CONFIRMATION = 'Оплата по счету № {} на сумму {} {} прошла успешно.'
PAYMENT_WAS_CREATED = (
    'Создан платежный документ № {}.\n'
    'Для оплаты перейдите по <a href="{}">ссылке</a> '
    'или нажмите:'
)


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
    admin_telegram_id, payment, payer_telegram_id, session
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
        session,
    )


async def send_payment_message(
    admin_telegram_id,
    payer_telegram_id,
    db_payment_id,
    yookassa_payment_id,
    yookassa_payment_url,
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
        return await send_successful_payment_message(
            [admin_telegram_id, payer_telegram_id], payment
        )
    return await send_failed_payment_message(
        [admin_telegram_id, payer_telegram_id], payment
    )


async def send_successful_payment_message(telegram_id_list, payment):
    for telegram_id in telegram_id_list:
        await bot.send_message(
            telegram_id,
            text=PAYMENT_CONFIRMATION.format(
                payment.id, payment.amount.value, payment.amount.currency
            ),
        )


async def send_failed_payment_message(telegram_id_list, payment):
    for telegram_id in telegram_id_list:
        await bot.send_message(
            telegram_id, text=PAYMENT_TIME_EXPIRED.format(payment.id)
        )
