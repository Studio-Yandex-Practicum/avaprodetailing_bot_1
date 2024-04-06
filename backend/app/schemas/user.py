import re
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, validator
from fastapi import Form


class UserCreate(BaseModel):

    phone_number: str
    telegram_id: Optional[str]
    first_name: str
    second_name: str
    last_name: str
    birth_date: date
    

    @classmethod
    async def as_form(
        cls,
        telegram_id: str = Form(...),
        phone_number: str = Form(...),
        first_name: str = Form(...),
        second_name: str = Form(...),
        last_name: str = Form(...),
        birth_date: date = Form(...)
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
            f'Пользователь {self.first_name} {self.second_name} {self.last_name} создан.'
        )


class UserUpdate(UserCreate):
    telegram_id: Optional[str]
    first_name: Optional[str]
    second_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[date]

    def __repr__(self):
        return (
            'Данныео пользователя: ',
            f'{self.first_name} ',
            f'{self.second_name} ',
            f'{self.last_name} '
            'обновлены'
        )
