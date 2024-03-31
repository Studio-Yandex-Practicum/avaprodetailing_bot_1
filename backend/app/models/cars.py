from app.core.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class Car(Base):
    id: int = Column(Integer, primary_key=True)
    brand: str = Column(String, nullable=False)
    model: str = Column(String, nullable=False)
    number_plate: str = Column(String, nullable=False)
    owner_id: str = Column(
        String, ForeignKey('user.id', name='fk_car_user_id_owner')
    )
