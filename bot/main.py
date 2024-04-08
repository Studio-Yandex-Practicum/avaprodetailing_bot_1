import asyncio
import aiohttp
import logging
from http import HTTPStatus
import os
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv
from messages import WECLOME_NEW_USER
from keyboards import registration_button

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

test_button = types.KeyboardButton(
    text='ya.ru',
    web_app=types.WebAppInfo(url='https://ya.ru')
)
test_button_1 = types.KeyboardButton(
    text='translate',
    web_app=types.WebAppInfo(url='https://translate.yandex.ru')
)
kb = types.ReplyKeyboardMarkup(
    keyboard=[[test_button, test_button_1]],
    resize_keyboard=True
)
# Для тестов
SITE_URL = 'http://127.0.0.1:8081'
SITE_URLs = 'https://127.0.0.1:8081'

# Для тестов


@dp.message(Command('start'))
async def starting(message: types.Message):
    telegarm_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{SITE_URL}/users/check_user/{telegarm_id}'
        ) as resp:
            if resp.status == HTTPStatus.NOT_FOUND:
                await message.answer(
                    WECLOME_NEW_USER,
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[
                            [await registration_button(SITE_URLs, telegarm_id)]
                        ],
                        resize_keyboard=True
                    )
                )
            elif resp.status == HTTPStatus.OK:
                response = await resp.json()
                print(response['is_admin'])
                await message.answer('Приветствую222!', reply_markup=kb)
            else:
                logging.ERROR('Problem: server returned %s', resp.status)
                await message.answer(
                    'У нас проводятся технические работы, попробуйте позже'
                )


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    file_handler = RotatingFileHandler(
        filename='bot.log',
        maxBytes=100000,
        backupCount=10,
        encoding='utf-8',
        mode='w'
    )
    logging.basicConfig(
        handlers=[file_handler],
        level=logging.INFO,
        format=(
            '%(asctime)s [%(levelname)s]: '
            '[%(funcName)s:%(lineno)d] - %(message)s'
        )
    )

    asyncio.run(main())
