import re
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator

from app.core.config import (
    ALLOWED_CHARS,
    LENGTH_NUMBER_PLATE_ERROR,
    MAX_LENGTH_BRAND_MODEL,
    MAX_LENGTH_BRAND_MODEL_ERROR,
    MIN_LENGTH_BRAND_MODEL_ERROR,
    MIN_LENGTH_STR,
    NUMBER_PLATE_ERROR,
    NUMBER_PLATE_FORMAT_ERROR,
    OWNER_TELEGRAM_ID_ERROR,
)
from app.schemas.history import CarHistoryDB


class CarDB(BaseModel):
    brand: str
    model: str
    number_plate: str

    class Config:
        from_attributes = True


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

    @validator('brand', 'model', pre=True)
    def validate_fields(cls, value: str):
        match value:
            case None:
                return None
            case _ if len(value) < MIN_LENGTH_STR:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=MIN_LENGTH_BRAND_MODEL_ERROR,
                )
            case _ if len(value) > MAX_LENGTH_BRAND_MODEL:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=MAX_LENGTH_BRAND_MODEL_ERROR,
                )
            case _:
                return value.upper()

    @validator('number_plate', pre=True)
    def validate(cls, value: str):
        match value:
            case None:
                return None
            case _ if not value:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=NUMBER_PLATE_ERROR,
                )
            case _ if len(value) < 8 or len(value) > 9:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=LENGTH_NUMBER_PLATE_ERROR,
                )
            case value if not re.match(
                f'[{ALLOWED_CHARS}]{{1}}\\d{{3}}'
                f'[{ALLOWED_CHARS}]{{2}}\\d{{2,3}}',
                value.upper(),
            ):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=NUMBER_PLATE_FORMAT_ERROR,
                )
            case _:
                return value.upper()


class CarCreateUser(CarUpdate):
    brand: str
    model: str
    number_plate: str


class CarCreate(CarCreateUser):
    owner_telegram_id: str

    @validator('owner_telegram_id', pre=True)
    def validate_owner_telegram_id(cls, value: str):
        match value:
            case None:
                return None
            case _ if not value:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=OWNER_TELEGRAM_ID_ERROR,
                )
            case _:
                return value
