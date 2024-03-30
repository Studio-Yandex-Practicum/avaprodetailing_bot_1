import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv

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


@dp.message(Command('start'))
async def starting(message: types.Message):
    await message.answer('Приветствую!', reply_markup=kb)


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
