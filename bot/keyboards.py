from aiogram.types import KeyboardButton, WebAppInfo, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from dotenv import load_dotenv

load_dotenv()


class Cars(CallbackData, prefix='car'):
    action: str
    car_id: int


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


async def edit_car_user_button(
    site_url: str,
    telegram_id: str,
    car_id: str
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Редактировать',
        web_app=WebAppInfo(
            url=f'{site_url}/cars/{telegram_id}/edit_car/{car_id}/edit_form'
        )
    )


async def delete_car_user_button(car_id: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Удалить',
        callback_data=Cars(action='delete', car_id=car_id).pack()
    )


async def create_car_user_button(
    site_url: str,
    telegram_id: str
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Создать',
        web_app=WebAppInfo(
            url=f'{site_url}/cars/{telegram_id}/add_car/add_form'
        )
    )
