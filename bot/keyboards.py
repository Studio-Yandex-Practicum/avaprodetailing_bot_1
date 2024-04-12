from aiogram.types import KeyboardButton, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

car_list = KeyboardButton(text='Список автомобилей')


async def registration_button(
        site_url: str, telegram_id: str
) -> KeyboardButton:
    return KeyboardButton(
        text='Регистрация',
        web_app=WebAppInfo(url=f'{site_url}/users/{telegram_id}')
    )


async def personal_acount_button(
    site_url: str,
    telegram_id: str,
    phone: str
) -> KeyboardButton:
    return KeyboardButton(
        text='Личный кабинет',
        web_app=WebAppInfo(url=f'{site_url}/users/{telegram_id}/patch/{phone}')
    )
