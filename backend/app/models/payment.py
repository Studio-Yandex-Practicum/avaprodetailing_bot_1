import enum
from datetime import datetime


from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)

from app.core.db import Base
from app.core.config import MAX_LENGTH_UUID4


class PaymentMethod(str, enum.Enum):
    online = 'online'
    cash = 'cash'


class Payment(Base):
    generated_payment_id: str = Column(
        String(MAX_LENGTH_UUID4),
        nullable=True,
        unique=True,
    )
    date: datetime = Column(DateTime, nullable=False, default=datetime.now)
    price: int = Column(Integer, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    admin_id: int = Column(
        Integer,
        ForeignKey(
            'user.id',
            name='fk_payment_admin_id_user',
        ),
    )
    payer_id: int = Column(
        Integer,
        ForeignKey(
            'user.id',
            name='fk_payment_payer_id_user',
        ),
    )
    is_paid: bool = Column(Boolean, nullable=False, default=False)
