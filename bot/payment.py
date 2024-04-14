import asyncio
import os
import time

import yookassa
from dotenv import load_dotenv

load_dotenv()

yookassa.Configuration.account_id = os.getenv('SHOP_ID')
yookassa.Configuration.secret_key = os.getenv('SHOP_TOKEN')

BOT_URL = os.getenv('BOT_URL')

CHECKOUT_TIME = 600  # время на оплату
PAYMENT_WAS_CREATED = (
    'Создан платежный документ № {}.\n'
    'Для оплаты перейдите по <a href="{}">ссылке</a> '
    'или нажмите:'
)
PAYMENT_CONFIRMATION = 'Оплата на сумму {} рублей прошла успешно.'
PAYMENT_TIME_EXPIRED = (
    'Время ожидания оплаты истекло. '
    'Попробуйте снова или обратитесь к администратору.'
)


async def create_payment(db_payment: dict):
    payment = yookassa.Payment.create(
        dict(
            amount=dict(value=db_payment['price'], currency='RUB'),
            description=f'Счет № {db_payment["id"]}',
            payment_method_data=dict(type='bank_card'),
            capture=True,
            metadata=dict(chat_id=db_payment['payer_telegram_id']),
            confirmation=dict(type='redirect', return_url=BOT_URL),
        ),
        idempotency_key=db_payment['generated_payment_id'],
    )
    return payment.id, payment.confirmation.confirmation_url


async def check_payment(payment_id: str):
    start_time = time.time()
    while time.time() - start_time < CHECKOUT_TIME:
        payment = yookassa.Payment.find_one(payment_id)
        if payment.paid:
            return PAYMENT_CONFIRMATION.format(payment.amount.value)
        else:
            await asyncio.sleep(5)
    if not payment.paid:
        return PAYMENT_TIME_EXPIRED


#  """ПРИМЕР: НАБОР ФУНКЦИЙ ДЛЯ ОБРАБОТКИ ПЛАТЕЖА ОНЛАЙН"""


#  @dp.callback_query(lambda query: query.data == 'online_pay')
#  async def process_online_pay(callback_query: types.CallbackQuery):
#      admin_telegram_id = callback_query.from_user.id
#      await bot.send_message(
#          admin_telegram_id, text=CHOSEN_PAY_METHOD.format(ONLINE_PAY_METHOD)
#      )
#      payment = await send_post_request(
#          f'{WHOOK}/payments/admin/{admin_telegram_id}',
#          data=dict(
#              price=333,
#              payment_method='online',
#              payer_telegram_id=  # telegram_id плательщика,
#          ),
#      )
#      payer_telegram_id = payment['payer_telegram_id']
#      payment_id, payment_url = await create_payment(payment)
#      await bot.send_message(
#          payer_telegram_id,
#          text=PAYMENT_WAS_CREATED.format(payment_id, payment_url),
#          parse_mode='HTML',
#          reply_markup=types.InlineKeyboardMarkup(
#              inline_keyboard=[
#                  [
#                      types.InlineKeyboardButton(
#                          text='ОПЛАТИТЬ',
#                          web_app=types.WebAppInfo(url=payment_url),
#                      )
#                  ]
#              ]
#          ),
#      )
#      await bot.send_message(
#          payer_telegram_id,
#          text=f'{await check_payment(payment_id, payer_telegram_id)}',
#      )
#      await bot.edit_message_reply_markup(
#          payer_telegram_id, callback_query.message.message_id
#      )
#
#
#  async def send_post_request(url: str, data: dict):
#      async with aiohttp.ClientSession() as session:
#          async with session.post(url=url, json=data) as response:
#              return await response.json()
