import re
from typing import Optional

from fastapi import Form
from pydantic import BaseModel, validator

from app.core.config import (
    ALLOWED_CHARS,
    LENGTH_NUMBER_PLATE_ERROR,
    MAX_LENGTH_BRAND_MODEL,
    MAX_LENGTH_BRAND_MODEL_ERROR,
    MIN_LENGTH_BRAND_MODEL_ERROR,
    MIN_LENGTH_STR,
    NUMBER_PLATE_FORMAT_ERROR,
)
from app.schemas.history import CarHistoryDB


class CarDB(BaseModel):
    brand: str
    model: str
    number_plate: str

    class Config:
        from_attributes = True


class CarListUser(CarDB):
    id: int


class CarListDBAdmin(CarDB):
    id: int
    owner_telegram_id: str

    class Config(CarDB.Config):
        pass


class CarDBAdmin(CarListDBAdmin):
    changes: list[CarHistoryDB]

    class Config(CarDB.Config):
        pass


class CarUpdate(CarDB):
    brand: Optional[str]
    model: Optional[str]
    number_plate: Optional[str]

    class Config:
        extra = 'forbid'

    @validator('brand', 'model')
    def validate_model(cls, value: str):
        match value:
            case None:
                return None
            case _ if len(value) < MIN_LENGTH_STR:
                raise ValueError(MIN_LENGTH_BRAND_MODEL_ERROR)
            case _ if len(value) > MAX_LENGTH_BRAND_MODEL:
                raise ValueError(MAX_LENGTH_BRAND_MODEL_ERROR)
            case _:
                return value.upper()

    @validator('number_plate')
    def validate(cls, value: str):
        match value:
            case None:
                return None
            case _ if len(value) < 8 or len(value) > 9:
                raise ValueError(LENGTH_NUMBER_PLATE_ERROR)
            case value if not re.match(
                f'[{ALLOWED_CHARS}]{{1}}\\d{{3}}'
                f'[{ALLOWED_CHARS}]{{2}}\\d{{2,3}}',
                value.upper(),
            ):
                raise ValueError(NUMBER_PLATE_FORMAT_ERROR)
            case _:
                return value.upper()


class CarCreate(CarUpdate):
    brand: str
    model: str
    number_plate: str
    owner_telegram_id: str

    class Config:
        orm_mode = True

    @classmethod
    async def as_form(
        cls,
        brand: str = Form(
            ...,
            title='Марка',
            min_length=MIN_LENGTH_STR,
            max_length=MAX_LENGTH_BRAND_MODEL
        ),
        model: str = Form(
            ...,
            title='Модель',
            min_length=MIN_LENGTH_STR,
            max_length=MAX_LENGTH_BRAND_MODEL
        ),
        number_plate: str = Form(..., title='Гос. Номер'),
        owner_telegram_id: str = Form(..., title='Владелец')

    ):
        return cls(
            brand=brand,
            model=model,
            number_plate=number_plate,
            owner_telegram_id=owner_telegram_id
        )


class CarCreateUser(CarUpdate):
    brand: str
    model: str
    number_plate: str

    @classmethod
    async def as_form(
        cls,
        brand: str = Form(
            ...,
            title='Марка',
            min_length=MIN_LENGTH_STR,
            max_length=MAX_LENGTH_BRAND_MODEL
        ),
        model: str = Form(
            ...,
            title='Модель',
            min_length=MIN_LENGTH_STR,
            max_length=MAX_LENGTH_BRAND_MODEL
        ),
        number_plate: str = Form(..., title='Гос. Номер')

    ):
        return cls(
            id=None,
            brand=brand,
            model=model,
            number_plate=number_plate
        )
