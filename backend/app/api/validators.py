import re
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user_crud

DUBLICATE_PHONE = 'Пользователь с таким номером телефона уже существует.'
DUBLICATE_TELEGRAM_ID = 'Пользователь с таким telegram_id уже существует'
INVALID_PHONE_NUMBER = (
    'Номер телефона должен состоять из цифр и иметь длину от 10 до 16 символов'
)
INVALID_BIRTH_DATE = 'Дата рождения не может быть больше текущей даты'


async def check_phone_dublicate(
        phone_number: str,
        telegram_id: str,
        session: AsyncSession
) -> None:
    user_id = await user_crud.get_user_id_by_phone_number(
        phone_number,
        session
    )
    if user_id and telegram_id != user_id:
        raise ValueError(DUBLICATE_PHONE)


async def check_telegram_id_dublicate(
        telegram_id: str,
        session: AsyncSession
) -> str:
    user = await user_crud.get_user_from_db(
        telegram_id, session
    )
    if user:
        raise ValueError()
    return telegram_id


def valid_phone_number(phone_number: str) -> str:
    phone_number = re.sub(r'[^\w\s]', '', phone_number)
    if not phone_number.isdigit() or not (10 <= len(phone_number) < 16):
        raise ValueError(
            INVALID_PHONE_NUMBER
        )
    return phone_number


def check_birth_date_less_current_data(birth_date: datetime) -> None:
    if birth_date > datetime.now().date():
        raise ValueError(INVALID_BIRTH_DATE)
