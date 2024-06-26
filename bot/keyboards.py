from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo
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
                f'{site_url}/payments/admin/{admin_telegram_id}/create_payment'
            )
        ),
    )


async def create_new_user_button(site_url: str, telegram_id: str):
    return KeyboardButton(
        text='Регистрация нового пользователя',
        web_app=WebAppInfo(
            url=(f'{site_url}/users/admin/{telegram_id}/add_user')
        ),
    )


async def edit_user_as_admin_button(site_url: str, telegram_id: str):
    return KeyboardButton(
        text='Просмотр/редактирование профиля клиента',
        web_app=WebAppInfo(
            url=(f'{site_url}/users/admin/{telegram_id}/user_info')
        ),
    )


async def loyalty_action_admin_button(site_url: str, telegram_id: str):
    return KeyboardButton(
        text='Начислить/списать бонусы',
        web_app=WebAppInfo(
            url=(f'{site_url}/loyality/admin/{telegram_id}/loyality_form')
        ),
    )


async def hire_fire_admin_button(site_url: str, telegram_id: str):
    return KeyboardButton(
        text='Назначить администратора',
        web_app=WebAppInfo(
            url=(f'{site_url}/users/superuser/{telegram_id}/hire_admin')
        ),
    )


async def get_admin_buttons(site_url: str, telegram_id: str):
    return [
        [
            await create_new_user_button(site_url, telegram_id),
            await edit_user_as_admin_button(site_url, telegram_id),
        ],
        [
            await create_payment_button(site_url, telegram_id),
            await loyalty_action_admin_button(site_url, telegram_id),
        ],
    ]


async def get_superuser_buttons(site_url: str, telegram_id: str):
    return [
        [
            await create_new_user_button(site_url, telegram_id),
            await edit_user_as_admin_button(site_url, telegram_id),
        ],
        [
            await hire_fire_admin_button(site_url, telegram_id),
        ],
        [
            await create_payment_button(site_url, telegram_id),
            await loyalty_action_admin_button(site_url, telegram_id),
        ],
    ]
