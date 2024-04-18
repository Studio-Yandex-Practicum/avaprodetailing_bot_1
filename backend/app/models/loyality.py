import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.config import DEFAULT_LOYALITY_VALUE
from app.core.db import Base


class LoyalityAction(str, enum.Enum):
    charge = 'начислено'
    write_off = 'списано'


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
    payment_id: int = Column(
        Integer,
        ForeignKey('payment.id', name='fk_loyality_payment_id_payment'),
        nullable=True,
    )
    payment = relationship(
        'Payment',
        back_populates='loyality',
    )
    action: LoyalityAction = Column(Enum(LoyalityAction), nullable=False)
    amount: int = Column(Integer, nullable=False)
    edited: bool = Column(Boolean, nullable=False, default=False)
    date: DateTime = Column(DateTime, nullable=False, default=datetime.now)
    exp_date: DateTime = Column(DateTime, nullable=False)
    changes = relationship('LoyalityHistory', backref='loyality')

    def __repr__(self):
        return (
            f'{self.action.capitalize()} {self.amount} баллов.\n'
            f'Пользователю {self.user_id} {self.action} '
            f'баллов: {abs(self.amount)}. '
            f'Дата начисления: {self.date.strftime("%d-%m-%Y")}. '
            f'Срок действия: {self.exp_date.strftime("%d-%m-%Y")}'
        )
