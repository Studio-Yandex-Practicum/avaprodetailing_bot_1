from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.payment import PaymentMethod  # asdas


class PaymentUpdate(BaseModel):
    is_paid: Optional[bool]

    class Config:
        extra = 'forbid'


class PaymentCreateAdmin(BaseModel):
    price: int
    payment_method: PaymentMethod

    class Config:
        extra = 'forbid'


class PaymentCreate(PaymentCreateAdmin):
    admin_id: int
    payer_id: int
    generated_payment_id: str

    class Config(PaymentCreateAdmin.Config):
        pass


class PaymentDBAdmin(PaymentCreate, PaymentUpdate):
    id: int
    date: datetime

    class Config:
        from_attributes = True
