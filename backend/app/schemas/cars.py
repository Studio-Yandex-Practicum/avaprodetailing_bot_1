import re
from typing import Optional

from pydantic import BaseModel, validator

ALLOWED_CHARS = 'АВЕКМНОРСТУХ'
LENGTH_NUMBER_PLATE = 'Длина номера автомобиля должна быть 8-9 символов.'
NUMBER_PLATE_FORMAT_ERROR = (
    'Неверный формат номера. '
    'Номер нужно вводить в формате А000АА00. Используйте кириллицу.'
)
MIN_LENGTH_BRAND_MODEL = 'Поле не может быть пустым.'
MIN_LENGTH_STR = 1


class CarDB(BaseModel):
    brand: str
    model: str
    number_plate: str

    class Config:
        from_attributes = True


class CarDBAdmin(CarDB):
    id: int
    owner_telegram_id: str

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
                raise ValueError(MIN_LENGTH_BRAND_MODEL)
            case _:
                return value.upper()

    @validator('number_plate')
    def validate(cls, value: str):
        match value:
            case None:
                return None
            case _ if len(value) < 8 or len(value) > 9:
                raise ValueError(LENGTH_NUMBER_PLATE)
            case value if not re.match(
                f'[{ALLOWED_CHARS}]{{1}}\\d{{3}}[{ALLOWED_CHARS}]{{2}}\\d{{2,3}}',
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
