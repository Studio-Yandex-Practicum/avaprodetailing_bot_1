from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.core.config import (
    MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_PHONE,
    MAX_LENGTH_USER_INFO_FIELDS,
)
from app.core.db import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(MAX_LENGTH_PHONE), unique=True)
    telegram_id = Column(String(MAX_LENGTH_USER_INFO_FIELDS), unique=True)
    first_name = Column(String(MAX_LENGTH_USER_INFO_FIELDS))
    second_name = Column(String(MAX_LENGTH_USER_INFO_FIELDS))
    last_name = Column(String(MAX_LENGTH_LAST_NAME))
    birth_date = Column(Date)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    car_history = relationship('CarHistory', backref='changed_by')
    changes = relationship(
        'UserHistory',
        foreign_keys='UserHistory.object_id',
        backref='user',
    )
    loyality_history = relationship(
        'LoyalityHistory',
        foreign_keys='LoyalityHistory.user_id',
        backref='user',
    )

    def __repr__(self):
        return (
            f'Номер телефона: {self.phone_number},'
            f'ФИО: {self.first_name} {self.second_name} {self.last_name}'
            f'Дата рождения: {self.birth_date}'
        )
