from datetime import datetime
from typing import Optional

from fastapi import Form
from pydantic import BaseModel

from app.models.payment import PaymentMethod


class PaymentUpdateIsPaid(BaseModel):
    is_paid: Optional[bool]

    class Config:
        extra = 'forbid'


class PaymentUpdateGeneratedPaymentId(BaseModel):
    generated_payment_id: Optional[str]

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

    @classmethod
    async def as_form(
        cls,
        price: int = Form(..., title='Цена'),
        payment_method: PaymentMethod = Form(..., title='Способ оплаты'),
        payer_id: str = Form(..., title='ID плательщика'),
        admin_id: str = Form(..., title='ID администратора'),
    ):
        return cls(
            price=price,
            payment_method=payment_method,
            payer_id=payer_id,
            admin_id=admin_id,
        )

    class Config(PaymentCreateAdmin.Config):
        pass


class PaymentCashCreate(
    PaymentCreate, PaymentUpdateGeneratedPaymentId, PaymentUpdateIsPaid
):

    class Config:
        extra = 'forbid'


class PaymentDBAdmin(PaymentCashCreate):
    id: int
    date: datetime

    class Config:
        from_attributes = True
