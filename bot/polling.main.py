import asyncio
import logging
import os
from datetime import datetime as dt
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import aiohttp
import qrcode.image.svg
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from dotenv import load_dotenv

from constants import (
    DT_FORMAT,
    FORMAT,
    LOYALITY_CHARGE_MESSAGE,
    LOYALITY_HISTORY_EMPTY,
    LOYALITY_WRITE_OFF_MESSAGE,
    SOMETHING_WENT_WRONG,
    TOTAL_HISTORY_OBJECTS,
)
from keyboards import (
    Cars,
    car_list,
    create_car_user_button,
    delete_car_user_button,
    edit_car_user_button,
    get_admin_buttons,
    get_superuser_buttons,
    personal_acount_button,
    registration_button,
    loyality_points_button,
    loyality_points_history_button,
    user_qr_code_button,
)
from messages import WELCOME_NEW_USER

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

SITE_URL = os.getenv('SITE_URL')


@dp.message(Command('start'))
async def starting(message: types.Message):
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
                                        telegram_id,
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
                elif response['is_admin'] and not response['is_superuser']:
                    await message.answer(
                        'Добро пожаловать!',
                        reply_markup=types.ReplyKeyboardMarkup(
                            keyboard=await get_admin_buttons(
                                SITE_URL, telegram_id
                            )
                        ),
                        resize_keyboard=True,
                    )
                elif not response['is_admin'] and response['is_superuser']:
                    await message.answer(
                        'Добро пожаловать!',
                        reply_markup=types.ReplyKeyboardMarkup(
                            keyboard=await get_superuser_buttons(
                                SITE_URL, telegram_id
                            )
                        ),
                        resize_keyboard=True,
                    )
            else:
                logging.error('Problem: server returned %s', response.status)
                await message.answer(
                    'У нас проводятся технические работы, попробуйте позже'
                )


@dp.message(F.web_app_data.via_bot)
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


@dp.message(F.text == 'Список автомобилей')
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


@dp.callback_query(Cars.filter(F.action == 'delete'))
async def delete_car(call: types.CallbackQuery, callback_data: Cars):
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            (
                f'{SITE_URL}/cars/{call.message.chat.id}'
                f'/delete_car/{callback_data.car_id}'
            )
        ) as response:
            if response.status == HTTPStatus.OK:
                response = await response.json()
                await call.message.answer(
                    'Машина {} {} {} успешно удалена.'.format(
                        response['brand'],
                        response['model'],
                        response['number_plate'],
                    )
                )
            else:
                await call.message.answer((await response.json())['detail'])


@dp.message(F.text == user_qr_code_button.text)
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


@dp.message(F.text == loyality_points_button.text)
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


@dp.message(F.text == loyality_points_history_button.text)
async def loyality_points_history(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/loyality/user/{message.from_user.id}/history'
        ) as response:
            data = await response.json()
            if response.status == HTTPStatus.OK:
                if not data:
                    return await message.answer(LOYALITY_HISTORY_EMPTY)
                data.sort(key=lambda x: x['date'], reverse=True)
                for loyality in data[:TOTAL_HISTORY_OBJECTS]:
                    if loyality['action'] == 'списание':
                        await message.answer(
                            LOYALITY_WRITE_OFF_MESSAGE.format(
                                abs(loyality['amount']),
                                dt.strptime(
                                    loyality['date'], DT_FORMAT
                                ).strftime(FORMAT),
                            )
                        )
                    else:
                        await message.answer(
                            LOYALITY_CHARGE_MESSAGE.format(
                                loyality['amount'],
                                dt.strptime(
                                    loyality['date'], DT_FORMAT
                                ).strftime(FORMAT),
                                dt.strptime(
                                    loyality['exp_date'], DT_FORMAT
                                ).strftime(FORMAT),
                            )
                        )
            else:
                await message.answer(SOMETHING_WENT_WRONG)


async def main():
    await dp.start_polling(bot)


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
