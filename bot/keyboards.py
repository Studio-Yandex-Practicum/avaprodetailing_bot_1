from aiogram.types import KeyboardButton, WebAppInfo, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from dotenv import load_dotenv

load_dotenv()


class Cars(CallbackData, prefix='car'):
    action: str
    car_id: int


car_list = KeyboardButton(text='Список автомобилей')
user_qr_code_button = KeyboardButton(text='Показать QR-код')
loyality_points_button = KeyboardButton(text='Накоплено баллов')
loyality_points_history_button = KeyboardButton(
    text='История по баллам лояльности'
)


async def universal_web_app_keyboard_button(
    text: str, url: str
) -> KeyboardButton:
    return KeyboardButton(text=text, web_app=WebAppInfo(url=url))


async def registration_button(
    site_url: str, telegram_id: str
) -> KeyboardButton:
    return KeyboardButton(
        text='Регистрация',
        web_app=WebAppInfo(url=f'{site_url}/users/{telegram_id}'),
    )


async def personal_acount_button(
    site_url: str, telegram_id: str, phone: str
) -> KeyboardButton:
    return KeyboardButton(
        text='Личный кабинет',
        web_app=WebAppInfo(
            url=f'{site_url}/users/{telegram_id}/patch/{phone}'
        ),
    )


async def edit_car_user_button(
    site_url: str, telegram_id: str, car_id: str
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Редактировать',
        web_app=WebAppInfo(
            url=f'{site_url}/cars/{telegram_id}/edit_car/{car_id}/edit_form'
        ),
    )


async def delete_car_user_button(car_id: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Удалить',
        callback_data=Cars(action='delete', car_id=car_id).pack(),
    )


async def create_car_user_button(
    site_url: str, telegram_id: str
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Создать',
        web_app=WebAppInfo(
            url=f'{site_url}/cars/{telegram_id}/add_car/add_form'
        ),
    )


async def create_payment_button(
    site_url: str, admin_telegram_id: str
) -> KeyboardButton:
    return KeyboardButton(
        text='Создать платеж',
        web_app=WebAppInfo(
            url=(
                f'{site_url}/payments/admin/{admin_telegram_id}'
                '/create_payment'
            )
        ),
    )


async def get_admin_buttons(site_url: str, telegram_id: str):
    return [
        [
            await universal_web_app_keyboard_button(
                text='Регистрация нового клиента',
                url=(f'{site_url}/users/admin/' f'{telegram_id}/add_user'),
            ),
            await universal_web_app_keyboard_button(
                text='Просмотр/редактирование аккаунта клиента',
                url=(f'{site_url}/users/admin/' f'{telegram_id}/user_info'),
            ),
        ],
        [
            await create_payment_button(site_url, telegram_id),
            await universal_web_app_keyboard_button(
                text='Начислить/списать баллы',
                url=(
                    f'{site_url}/loyality/admin/'
                    f'{telegram_id}/'
                    'loyality_form'
                ),
            ),
        ],
    ]


async def get_superuser_buttons(site_url: str, telegram_id: str):
    return [
        [
            await universal_web_app_keyboard_button(
                'Регистрация нового пользователя',
                url=(f'{site_url}/users/admin/' f'{telegram_id}/add_user'),
            ),
            await universal_web_app_keyboard_button(
                'Просмотр/редактирование аккаунта пользователя',
                url=(f'{site_url}/users/admin/' f'{telegram_id}/user_info'),
            ),
        ],
    ]
