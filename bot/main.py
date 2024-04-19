import asyncio
import logging

import os
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import aiohttp
from aiohttp import web
import qrcode.image.svg
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import (SimpleRequestHandler,
                                            setup_application)

from dotenv import load_dotenv

from keyboards import (
    Cars,
    car_list,
    create_car_user_button,
    delete_car_user_button,
    edit_car_user_button,
    personal_acount_button,
    registration_button,
    user_qr_code_button,
    loyality_points_button,
    loyality_points_history_button,
    universal_web_app_keyboard_button,
    user_qr_code_button,
)
from messages import WELCOME_NEW_USER

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

SITE_URL = os.getenv('SITE_URL')
WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST')
WEB_SERVER_PORT = int(os.getenv('WEB_SERVER_PORT'))

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/users/check_user/{telegram_id}'
        ) as response:
            if response.status == HTTPStatus.NOT_FOUND:
                await message.answer(
                    WELCOME_NEW_USER,
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[
                            [await registration_button(SITE_URL, telegram_id)]
                        ],
                        resize_keyboard=True,
                    ),
                )
            elif response.status == HTTPStatus.OK:
                response = await response.json()
                if not response['is_admin'] and not response['is_superuser']:
                    await message.answer(
                        'С возвращением!',
                        reply_markup=types.ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    await personal_acount_button(
                                        SITE_URL,
                                        message.from_user.id,
                                        response['phone_number'],
                                    ),
                                    car_list,
                                    user_qr_code_button,
                                ],
                                [
                                    loyality_points_button,
                                    loyality_points_history_button,
                                ],
                            ]
                        ),
                        resize_keyboard=True,
                    )
                elif response['is_admin'] and response['is_superuser']:
                    await message.answer(
                        'Добро пожаловать.',
                        reply_markup=types.ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    await universal_web_app_keyboard_button(
                                        'Регистрация нового клиента',
                                        url=(
                                            f'{SITE_URL}/users/admin/'
                                            f'{message.from_user.id}/add_user'
                                        ),
                                    ),
                                    await universal_web_app_keyboard_button(
                                        'Просмотр/редактирование клиента',
                                        url=(
                                            f'{SITE_URL}/users/admin/'
                                            f'{message.from_user.id}/user_info'
                                        ),
                                    ),
                                ],
                                [
                                    await create_payment_button(
                                        SITE_URL, telegram_id
                                    ),
                                    await universal_web_app_keyboard_button(
                                        text='Начислить/списать баллы',
                                        url=(
                                            f'{SITE_URL}/loyality/admin/'
                                            f'{message.from_user.id}/'
                                            'loyality_form'
                                        ),
                                    ),
                                ],
                            ]
                        ),
                        resize_keyboard=True,
                    )
            else:
                logging.error('Problem: server returned %s', response.status)
                await message.answer(
                    'У нас проводятся технические работы, попробуйте позже'
                )


@router.message(F.web_app_data.via_bot)
async def web_app2(message: types.Message):
    if message.web_app_data.data == 'Car added':
        await message.answer('Car added')
    if message.web_app_data.data == 'Registartion Success':
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{SITE_URL}/users/check_user/{message.from_user.id}'
            ) as response:
                if response.status == HTTPStatus.OK:
                    response = await response.json()
                    if (
                        not response['is_admin']
                        and not response['is_superuser']
                    ):
                        await message.answer(
                            'Регистрация успешно пройдена',
                            reply_markup=types.ReplyKeyboardMarkup(
                                keyboard=[
                                    [
                                        await personal_acount_button(
                                            SITE_URL,
                                            message.from_user.id,
                                            response['phone_number'],
                                        ),
                                        car_list,
                                        user_qr_code_button,
                                    ],
                                    [
                                        loyality_points_button,
                                        loyality_points_history_button,
                                    ],
                                ]
                            ),
                            resize_keyboard=True,
                        )

                    await message.answer(str(response))
                else:
                    logging.error(
                        'Problem: server returned %s', response.status
                    )
                    await message.answer(
                        'У нас проводятся технические работы, попробуйте позже'
                    )


@router.message(F.text == 'Список автомобилей')
async def get_car_list(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/cars/{message.from_user.id}'
        ) as response:
            if (
                response.status == HTTPStatus.OK
                and len(await response.json()) > 0
            ):
                [
                    await message.answer(
                        (
                            f'Марка: {car["brand"]}\n Модель: {car["model"]}\n'
                            f'Гос. Номер: {car["number_plate"]}'
                        ),
                        reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    await edit_car_user_button(
                                        SITE_URL,
                                        message.from_user.id,
                                        car["id"],
                                    ),
                                    await delete_car_user_button(car["id"]),
                                ]
                            ]
                        ),
                    )
                    for car in await response.json()
                ]
            await message.answer(
                'Добавить машину',
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            await create_car_user_button(
                                SITE_URL, message.from_user.id
                            )
                        ]
                    ]
                ),
            )


@router.callback_query(Cars.filter(F.action == 'delete'))
async def delete_car(call: types.CallbackQuery, callback_data: Cars):
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            (
                f'{SITE_URL}/cars/{call.message.chat.id}'
                f'/delete_car/{callback_data.car_id}'
            )
        ) as response:
            if response.status == HTTPStatus.OK:
                await call.message.answer('Машина удалена')


@router.message(F.text == user_qr_code_button.text)
async def user_qr_code(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/users/check_user/{message.from_user.id}'
        ) as response:
            phone_number = (await response.json())['phone_number']
            img = qrcode.make(phone_number)
            img.save(f'{phone_number}.png')
            with open(f'{phone_number}.png', 'rb') as file:
                await message.answer_photo(
                    types.BufferedInputFile(
                        file.read(), filename='qr_code.png'
                    )
                )
            os.remove(f'{phone_number}.png')


@router.message(F.text == loyality_points_button.text)
async def loyality_points(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/loyality/user/{message.from_user.id}/'
        ) as response:
            data = await response.json()
            if response.status == HTTPStatus.OK:
                await message.answer(
                    f'У вас накоплено баллов: {data["count"]}'
                )
            elif response.status == HTTPStatus.NOT_FOUND:
                await message.answer(data['count'])
            else:
                await message.answer('Что-то пошло не так. Попробуйте позже')


@router.message(F.text == 'Список пользователей')
async def get_user_list(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/users/admin/{message.from_user.id}'
        ) as response:
            if (
                response.status == HTTPStatus.OK
                and len(await response.json()) > 0
            ):
                [
                    await message.answer(
                        (
                            f'ФИО: {user["last_name"]} {user["first_name"]} '
                            f'{user["second_name"]}\n'
                            f'Дата рождения: {user["birth_date"]}\n'
                            f'Номер телефона: {user["phone_number"]}'
                        ),
                        reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    await edit_user_admin_button(
                                        SITE_URL,
                                        message.from_user.id,
                                        user['telegram_id'],
                                        user['phone_number'],
                                    )
                                ]
                            ]
                        ),
                    )
                    for user in await response.json()
                ]


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{SITE_URL}{WEBHOOK_PATH}",
                          secret_token=WEBHOOK_SECRET)


async def main():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    await web._run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == '__main__':
    file_handler = RotatingFileHandler(
        filename='bot.log',
        maxBytes=100000,
        backupCount=10,
        encoding='utf-8',
        mode='w',
    )
    logging.basicConfig(
        handlers=[file_handler],
        level=logging.INFO,
        format=(
            '%(asctime)s [%(levelname)s]: '
            '[%(funcName)s:%(lineno)d] - %(message)s'
        ),
    )
    asyncio.run(main())
