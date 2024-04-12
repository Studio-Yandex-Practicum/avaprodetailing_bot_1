from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.config import HISTORY_MAX_LENGTH_STRING
from app.core.db import Base


class HistoryBase(Base):
    __abstract__ = True
    date = Column(DateTime, default=datetime.now)
    old_data = Column(String(HISTORY_MAX_LENGTH_STRING), nullable=False)
    new_data = Column(String(HISTORY_MAX_LENGTH_STRING), nullable=False)


class CarHistory(HistoryBase):
    changed_by_id: int = Column(
        Integer,
        ForeignKey(
            'user.id',
            name='fk_carhistory_changed_by_id_user',
            ondelete='CASCADE',
        ),
    )
    object_id: int = Column(
        Integer,
        ForeignKey(
            'car.id', name='fk_carhistory_car_id_car', ondelete='CASCADE'
        ),
    )


class UserHistory(HistoryBase):
    changed_by_id: int = Column(
        Integer,
        ForeignKey('user.id', name='fk_userhistory_changed_by_id_user'),
    )
    object_id: int = Column(
        Integer, ForeignKey('user.id', name='fk_userhistory_object_id_user')
    )


class LoyalitySettingsHistory(HistoryBase):
    changed_by_id: int = Column(
        Integer,
        ForeignKey(
            'user.id', name='fk_loyalitysettingshistory_changed_by_id_user'
        ),
    )
    object_id: int = Column(
        Integer,
        ForeignKey(
            'loyalitysettings.id',
            name='fk_loyalitysettingshistory_object_id_loyalitysettings',
        ),
    )


class LoyalityHistory(Base):
    date = Column(DateTime, default=datetime.now)
    new_data = Column(String(HISTORY_MAX_LENGTH_STRING), nullable=False)
    admin_id: int = Column(
        Integer,
        ForeignKey('user.id', name='fk_loyalityhistory_admin_id_user'),
    )
    user_id: int = Column(
        Integer,
        ForeignKey('user.id', name='fk_loyalityhistory_user_id_user'),
    )
    loyality_id: int = Column(
        Integer,
        ForeignKey(
            'loyality.id', name='fk_loyalityhistory_loyality_id_loyality'
        ),
    )
