import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import User
from sqlalchemy import select
from sqlalchemy import func, exists

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

test_button = types.KeyboardButton(
    text='ya.ru',
    web_app=types.WebAppInfo(url='https://20f0-95-25-72-15.ngrok-free.app/')
)
test_button_1 = types.KeyboardButton(
    text='translate',
    web_app=types.WebAppInfo(url='https://translate.yandex.ru')
)
kb = types.ReplyKeyboardMarkup(
    keyboard=[[test_button, test_button_1]],
    resize_keyboard=True
)


async def count_users():
    async with sessionmaker() as session:
        result = await session.execute(func.count(User.id))
        return result.scalar()


async def check_user(tg_id: int) -> bool:
    async with sessionmaker() as session:
        result = await session.execute(
            select(exists().where(User.telegram_id == tg_id))
        )
        return result.scalar()


@dp.message(Command('start'))
async def starting(message: types.Message):
    if await check_user(message.from_user.id):
        await message.answer('User already exists')
    else:
        await message.answer('Приветствую!', reply_markup=kb)
    await message.answer(str(message.from_user.id))
    await message.answer(str(await count_users()))


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
    engine = create_async_engine(os.getenv('SQLITE_DATABASE_URL'), echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(main())
