from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.config import DEFAULT_LOYALITY_VALUE
from app.core.db import Base


class LoyalitySettings(Base):
    default_value: int = Column(
        Integer, nullable=False, default=DEFAULT_LOYALITY_VALUE
    )
    changes = relationship(
        'LoyalitySettingsHistory',
        backref='loyality_settings',
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'1 бонусный балл начисляется за {self.default_value} рублей.'


class Loyality(Base):
    user_id: int = Column(
        Integer, ForeignKey('user.id', name='fk_loyality_user_id_user')
    )
    amount: int = Column(Integer, nullable=False)
    edited: bool = Column(Boolean, nullable=False, default=False)
    date: DateTime = Column(DateTime, nullable=False, default=datetime.now)
    exp_date: DateTime = Column(DateTime, nullable=False)
    changes = relationship('LoyalityHistory', backref='loyality')

    def __repr__(self):
        action = 'начислено'
        if self.amount < 0:
            action = 'списано'
        return (
            f'{action.capitalize()} {self.amount} баллов.\n'
            f'Пользователю {self.user_id} {action} {self.amount} баллов. '
            f'Дата начисления: {self.date.strftime("%d-%m-%Y")}. '
            f'Срок действия: {self.exp_date.strftime("%d-%m-%Y")}'
        )
