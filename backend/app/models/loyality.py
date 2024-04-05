from sqlalchemy import Column, DateTime, Integer, ForeignKey, Boolean
from app.core.db import Base
from datetime import datetime as dt
from datetime import timedelta


class LoyalitySettings(Base):
    default_value: int = Column(Integer, nullable=False, default=100)

    def __repr__(self):
        return f'Один балл начисляется за {self.default_value} рублей'


class Loyality(Base):
    user_id: int = Column(
        Integer,
        ForeignKey('user.id', name='fk_loyality_user_id_user')
    )
    amount: int = Column(Integer, nullable=False)
    edited: bool = Column(Boolean, nullable=False, default=False)
    date: DateTime = Column(DateTime, nullable=False, default=dt.now())
    exp_date: DateTime = Column(
        DateTime,
        nullable=False,
        default=dt.now() + timedelta(days=365)
    )

    def __repr__(self):
        if self.amount >0:
            return f'Пользователю {} начислено {} '
