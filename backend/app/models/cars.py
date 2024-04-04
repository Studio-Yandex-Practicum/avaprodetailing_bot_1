# from typing import Optional

from sqlalchemy import Column, String  # ForeignKey,
from sqlalchemy.orm import relationship

from app.core.db import Base


class Car(Base):
    brand: str = Column(String, nullable=False)
    model: str = Column(String, nullable=False)
    number_plate: str = Column(String, nullable=False, unique=True)
    # owner_telegram_id: Optional[str] = Column(
    #     String,
    #     ForeignKey('user.telegram_id', name='fk_car_user_telegram_id_owner'),
    #     nullable=True,
    # )
    # owner = relationship('User', back_populates='cars')

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'brand={self.brand}, model={self.model}, '
            f'number_plate{self.number_plate})'
            # , owner_id={self.owner_telegram_id})'
        )
