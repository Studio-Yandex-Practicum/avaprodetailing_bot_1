from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String

from app.core.config import MAX_LENGTH_BRAND_MODEL, MAX_LENGTH_NUMBER_PLATE
from app.core.db import Base


class Car(Base):
    brand: str = Column(String(MAX_LENGTH_BRAND_MODEL), nullable=False)
    model: str = Column(String(MAX_LENGTH_BRAND_MODEL), nullable=False)
    number_plate: str = Column(
        String(MAX_LENGTH_NUMBER_PLATE), nullable=False, unique=True
    )
    changes = relationship(
        'CarHistory', backref='car', cascade='all, delete-orphan'
    )
    owner_telegram_id: str = Column(
        String,
        ForeignKey(
            'user.telegram_id',
            name='fk_car_owner_telegram_id_user',
            ondelete='CASCADE',
        ),
        nullable=True,
    )

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'brand={self.brand}, model={self.model}, '
            f'number_plate{self.number_plate})'
        )
