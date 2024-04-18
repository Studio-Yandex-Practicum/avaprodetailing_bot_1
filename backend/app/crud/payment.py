from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Payment


class CRUDPayments(CRUDBase):

    async def get_user_payments(
        self, payer_telegram_id: str, session: AsyncSession
    ):
        return (
            (
                await session.execute(
                    select(Payment).where(
                        Payment.payer_telegram_id == payer_telegram_id
                    )
                )
            )
            .scalars()
            .all()
        )

    async def get_payment_by_uuid(self, uuid: str, session: AsyncSession):
        return (
            (
                await session.execute(
                    select(Payment).where(Payment.generated_payment_id == uuid)
                )
            )
            .scalars()
            .first()
        )


payments_crud = CRUDPayments(Payment)
