import asyncio
import os
import time
from uuid import uuid4

import yookassa
from dotenv import load_dotenv

load_dotenv()

yookassa.Configuration.account_id = os.getenv('SHOP_ID')
yookassa.Configuration.secret_key = os.getenv('SHOP_TOKEN')

BOT_URL = os.getenv('BOT_URL')

CHECKOUT_TIME = 600  # время на оплату, установленное ЮКассой


async def create_payment(db_payment, payer_telegram_id):
    payment = yookassa.Payment.create(
        dict(
            amount=dict(value=db_payment.price, currency='RUB'),
            description=f'Платеж по счету № {db_payment.id}',
            payment_method_data=dict(type='bank_card'),
            capture=True,
            metadata=dict(chat_id=payer_telegram_id),
            confirmation=dict(type='redirect', return_url=BOT_URL),
        ),
        idempotency_key=uuid4().__str__(),
    )
    return (
        payment.id,
        payment.confirmation.confirmation_url,
        payment.amount.value,
    )


async def check_payment(payment_id: str):
    start_time = time.time()
    while time.time() - start_time < CHECKOUT_TIME:
        payment = yookassa.Payment.find_one(payment_id)
        if payment.paid:
            return True, payment
        else:
            await asyncio.sleep(5)
    if not payment.paid:
        return False, payment
