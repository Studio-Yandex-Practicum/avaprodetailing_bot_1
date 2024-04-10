from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer

from app.core.config import DEFAULT_LOYALITY_VALUE
from app.core.db import Base


class LoyalitySettings(Base):
    default_value: int = Column(
        Integer,
        nullable=False,
        default=DEFAULT_LOYALITY_VALUE
    )

    def __repr__(self):
        return f'Один балл начисляется за {self.default_value} рублей'


class Loyality(Base):
    user_id: int = Column(
        Integer,
        ForeignKey('user.id', name='fk_loyality_user_id_user')
    )
    amount: int = Column(Integer, nullable=False)
    edited: bool = Column(Boolean, nullable=False, default=False)
    date: DateTime = Column(DateTime, nullable=False, default=datetime.now)
    exp_date: DateTime = Column(DateTime, nullable=False)

    def __repr__(self):
        action = 'начислено'
        if self.amount < 0:
            action = 'списано'
        return (
            f'Пользователю {action} {self.amount} баллов. '
            f'Пользователю {self.user_id} {action} {self.amount} баллов. '
            f'Дата: {self.date.strftime("%d-%m-%Y")}. Истекает: '
            f'{self.exp_date.strftime("%d-%m-%Y")}'
        )