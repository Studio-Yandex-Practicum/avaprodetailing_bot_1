import re
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.cars import cars_crud
from app.crud.user import user_crud
from app.models import Car
from app.schemas.cars import CarCreate, CarUpdate

CAR_NOT_FOUND = 'Автомобиль в базе данных не найден.'
CAR_WITH_NUMBER_EXISTS = 'Автомобиль с таким номером уже есть в базе данных.'

USER_NOT_FOUND = 'Пользователь не найден.'

NOT_ADMIN_OR_SUPERUSER = 'Действие доступно только администратору.'
FOREIGN_CAR = 'Вы не можете изменить или удалить чужой автомобиль.'
LAST_ONE_CAR = (
    'Последний автомобиль нельзя удалить. Обратитесь к администратору.'
)

ALLOWED_CHARS = 'АВЕКМНОРСТУХ'
LENGTH_NUMBER_PLATE = 'Длина номера автомобиля должна быть 8-9 символов.'
NUMBER_PLATE_FORMAT_ERROR = (
    'Неверный формат номера. '
    'Номер нужно вводить в формате А000АА00. Используйте кириллицу.'
)

ERROR_LENGTH_BRAND_MODEL = 'Поле не может быть пустым.'
MIN_LENGTH_STR = 1
MIN_LENGTH_NUMBER_PLATE = 8
MAX_LENGTH_NUMBER_PLATE = 9


async def check_car_exists(car_id: int, session: AsyncSession) -> None:
    if await cars_crud.get(car_id, session) is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=CAR_NOT_FOUND
        )


async def check_user_exists(telegram_id: str, session: AsyncSession) -> None:
    if await user_crud.get_user_by_telegram_id(telegram_id, session) is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=USER_NOT_FOUND
        )


async def check_length_user_car_list(
    telegram_id: str, session: AsyncSession
) -> None:
    if len(await cars_crud.get_my_cars(telegram_id, session)) == 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=LAST_ONE_CAR,
        )


async def check_user_is_owner(car: Car, telegram_id: str) -> None:
    if car.owner_telegram_id != telegram_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=FOREIGN_CAR,
        )


async def check_user_is_admin_or_superuser(
    telegram_id: str, session: AsyncSession
) -> None:
    user = await user_crud.get_user_by_telegram_id(telegram_id, session)
    if not (user.is_superuser or user.is_admin):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=NOT_ADMIN_OR_SUPERUSER
        )


async def check_user_before_car_edit(
    car: Car, telegram_id: str, session: AsyncSession
) -> None:
    if not await check_user_is_admin_or_superuser(telegram_id, session):
        await check_user_is_owner(car, telegram_id)


async def check_user_before_car_delete(
    car: Car, telegram_id: str, session: AsyncSession
) -> None:
    if not await check_user_is_admin_or_superuser(telegram_id, session):
        await check_user_is_owner(car, telegram_id)
        await check_length_user_car_list(telegram_id, session)


async def check_number_plate_duplicate(
    number_plate, session: AsyncSession
) -> None:
    if await cars_crud.get_car_by_number(number_plate, session):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=CAR_WITH_NUMBER_EXISTS
        )


async def check_car_data_before_create(
    telegram_id: str, car_data: CarCreate, session: AsyncSession
) -> None:
    await check_user_exists(car_data.owner_telegram_id, session)
    if telegram_id != car_data.owner_telegram_id:
        await check_user_is_admin_or_superuser(telegram_id, session)
    if len(car_data.brand) < MIN_LENGTH_STR:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_LENGTH_BRAND_MODEL
        )
    if len(car_data.model) < MIN_LENGTH_STR:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_LENGTH_BRAND_MODEL
        )
    if car_data.number_plate is not None:
        validate_number_plate(car_data.number_plate)
        await check_number_plate_duplicate(
            (car_data.number_plate).upper(), session
        )


async def check_car_before_edit(
    car_id: int, update_data: CarUpdate, session: AsyncSession
) -> None:
    car_to_edit = await cars_crud.get(car_id, session)
    if update_data.number_plate is not None:
        validate_number_plate(update_data.number_plate)
        number_plate = (car_to_edit.number_plate).upper()
        if number_plate != car_to_edit.number_plate:
            await check_number_plate_duplicate(number_plate, session)


# Для ручки добавления/изменения автомобиля для получения текста ошибки на фронтенд
def validate_number_plate(number_plate) -> None:
    if (
        len(number_plate) < MIN_LENGTH_NUMBER_PLATE
        or len(number_plate) > MAX_LENGTH_NUMBER_PLATE
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=LENGTH_NUMBER_PLATE,
        )
    if not re.match(
        f'[{ALLOWED_CHARS}]{{1}}\\d{{3}}[{ALLOWED_CHARS}]{{2}}\\d{{2,3}}',
        number_plate.upper(),
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NUMBER_PLATE_FORMAT_ERROR,
        )
