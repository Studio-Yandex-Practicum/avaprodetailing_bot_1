from datetime import datetime
from typing import Optional

from fastapi import Form
from pydantic import BaseModel


class UserCreate(BaseModel):
    phone_number: str
    telegram_id: str
    first_name: str
    second_name: str
    last_name: str
    birth_date: datetime

    @classmethod
    async def as_form(
        cls,
        telegram_id: str = Form(..., title='Telegram ID'),
        phone_number: str = Form(..., title='Номер телефона'),
        first_name: str = Form(..., title='Имя'),
        second_name: str = Form(..., title='Отчество'),
        last_name: str = Form(..., title='Фамилия'),
        birth_date: datetime = Form(..., title='Дата рождения')
    ):
        return cls(
            phone_number=phone_number,
            telegram_id=telegram_id,
            first_name=first_name,
            second_name=second_name,
            last_name=last_name,
            birth_date=birth_date
        )

    def __repr__(self):
        return (
            'Пользователь: '
            f'{self.first_name}'
            f'{self.second_name}'
            f'{self.last_name}'
            'создан.'
        )


class CheckedUser(BaseModel):
    telegram_id: Optional[str]
    is_admin: Optional[bool]
    is_superuser: Optional[bool]
    phone_number: Optional[str]

    class Config:
        extra = 'forbid'
        from_attributes = True


class UserUpdate(UserCreate):

    def __repr__(self):
        return (
            'Данныео пользователя: ',
            f'{self.first_name} ',
            f'{self.second_name} ',
            f'{self.last_name} '
            'обновлены'
        )


class UserFromDB(UserCreate):

    class Config:
        from_attributes = True
