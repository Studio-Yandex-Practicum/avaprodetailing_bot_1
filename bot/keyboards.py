from aiogram.types import KeyboardButton, WebAppInfo
from dotenv import load_dotenv
# import os

load_dotenv()


async def registration_button(
        site_url: str, telegram_id: str
) -> KeyboardButton:
    return KeyboardButton(
        text='Регистрация',
        web_app=WebAppInfo(url=f'{site_url}/users/{telegram_id}')
    )
