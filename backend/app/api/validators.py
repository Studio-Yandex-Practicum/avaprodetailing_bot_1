
import re
from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import (
    ALLOWED_CHARS,
    LENGTH_NUMBER_PLATE_ERROR,
    MAX_LENGTH_BRAND_MODEL,
    MAX_LENGTH_BRAND_MODEL_ERROR,
    MAX_LENGTH_NUMBER_PLATE,
    MIN_LENGTH_BRAND_MODEL_ERROR,
    MIN_LENGTH_NUMBER_PLATE,
    MIN_LENGTH_STR,
    NUMBER_PLATE_FORMAT_ERROR,
)
from app.crud.cars import cars_crud
from app.crud.user import user_crud
from app.models import Car
from app.schemas.cars import CarCreate, CarUpdate

CAR_NOT_FOUND = 'Автомобиль в базе данных не найден.'
CAR_WITH_NUMBER_EXISTS = 'Автомобиль с таким номером уже есть в базе данных.'

USER_NOT_FOUND = 'Пользователь не найден.'

NOT_ADMIN_OR_SUPERUSER = 'Действие доступно только администратору.'
FOREIGN_CAR_ERROR = (
    'Вы не можете добавить, изменить или удалить чужой автомобиль.'
)
LAST_ONE_CAR = (
    'Последний автомобиль нельзя удалить. Обратитесь к администратору.'
)
DUBLICATE_PHONE = 'Пользователь с таким номером телефона уже существует.'
DUBLICATE_TELEGRAM_ID = 'Пользователь с таким telegram_id уже существует'
INVALID_PHONE_NUMBER = (
    'Номер телефона должен состоять из цифр и иметь длину от 10 до 16 символов'
)
INVALID_BIRTH_DATE = 'Дата рождения не может быть больше текущей даты'


async def check_car_exists(car_id: int, session: AsyncSession) -> None:
    if not await cars_crud.get(car_id, session):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=CAR_NOT_FOUND
        )


async def check_user_exists(telegram_id: str, session: AsyncSession) -> None:
    if not await user_crud.get_user_by_telegram_id(telegram_id, session):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND
        )


async def check_admin_user(telegram_id: str, session: AsyncSession) -> None:
    await check_user_exists(telegram_id, session)
    await check_user_is_admin_or_superuser(telegram_id, session)


async def check_length_user_car_list(
    telegram_id: str, session: AsyncSession
) -> None:
    if len(await cars_crud.get_my_cars(telegram_id, session)) == 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=LAST_ONE_CAR,
        )


async def check_user_is_owner(
    data: Car, telegram_id: str, session: AsyncSession
) -> None:
    await check_user_exists(telegram_id, session)
    await check_user_exists(data.owner_telegram_id, session)
    if data.owner_telegram_id != telegram_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=FOREIGN_CAR_ERROR,
        )


async def check_user_is_admin_or_superuser(
    telegram_id: str, session: AsyncSession
) -> None:
    user = await user_crud.get_user_by_telegram_id(telegram_id, session)
    if not (user.is_superuser or user.is_admin):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=NOT_ADMIN_OR_SUPERUSER
        )


async def check_car_data_before_create(
    car_data: CarCreate, session: AsyncSession
) -> None:
    await validate_car_fields(car_data)
    if car_data.number_plate:
        await validate_number_plate(car_data.number_plate)
        await check_number_plate_duplicate(car_data.number_plate, session)


async def check_car_before_edit(
    car_id: int, update_data: CarUpdate, session: AsyncSession
) -> None:
    car_to_edit = await cars_crud.get(car_id, session)
    await validate_car_fields(update_data)
    if update_data.number_plate:
        await validate_number_plate(update_data.number_plate)
        if update_data.number_plate != car_to_edit.number_plate:
            await check_number_plate_duplicate(
                update_data.number_plate, session
            )


async def check_number_plate_duplicate(
    number_plate, session: AsyncSession
) -> None:
    if await cars_crud.get_car_by_number(number_plate, session):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=CAR_WITH_NUMBER_EXISTS
        )


async def validate_car_fields(data) -> None:
    await validate_field(data, 'brand')
    await validate_field(data, 'model')


async def validate_field(data, field: str) -> None:
    value = getattr(data, field)
    if value:
        if len(value) < MIN_LENGTH_STR:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=MIN_LENGTH_BRAND_MODEL_ERROR,
            )
        if len(value) > MAX_LENGTH_BRAND_MODEL:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=MAX_LENGTH_BRAND_MODEL_ERROR,
            )


async def validate_number_plate(number_plate) -> None:
    if (
        len(number_plate) < MIN_LENGTH_NUMBER_PLATE
        or len(number_plate) > MAX_LENGTH_NUMBER_PLATE
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=LENGTH_NUMBER_PLATE_ERROR,
        )
    if not re.match(
        f'[{ALLOWED_CHARS}]{{1}}\\d{{3}}[{ALLOWED_CHARS}]{{2}}\\d{{2,3}}',
        number_plate,
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NUMBER_PLATE_FORMAT_ERROR,
        )


async def check_phone_dublicate(
        phone_number: str,
        telegram_id: str,
        session: AsyncSession
) -> None:
    user_id = await user_crud.get_user_by_phone_number(
        phone_number,
        session
    )
    if user_id and telegram_id != user_id.telegram_id:
        raise ValueError(DUBLICATE_PHONE)


async def check_telegram_id_dublicate(
        telegram_id: str,
        current_telegram_id: str,
        session: AsyncSession
) -> str:
    user = await user_crud.get_user_by_telegram_id(
        current_telegram_id, session
    )
    if user and current_telegram_id != user.telegram_id:
        raise ValueError(DUBLICATE_TELEGRAM_ID)
    return telegram_id


def valid_phone_number(phone_number: str) -> str:
    phone_number = re.sub(r'[^\w\s]', '', phone_number)
    if not phone_number.isdigit() or not (10 <= len(phone_number) < 16):
        raise ValueError(
            INVALID_PHONE_NUMBER
        )
    return phone_number


def check_birth_date_less_current_data(birth_date: datetime) -> None:
    if birth_date > datetime.now():
        raise ValueError(INVALID_BIRTH_DATE)
