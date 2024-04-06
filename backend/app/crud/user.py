from typing import Optional


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase

from app.models import User


class CRUDUser(CRUDBase):
    async def get_user_by_telegram_id(
        self, telegram_id: str, session: AsyncSession
    ) -> Optional[int]:
        return (
            (
                await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
            )
            .scalars()
            .first()
        )

    async def get_user_by_phone_number(
        self, phone_number: str, session: AsyncSession
    ) -> Optional[int]:
        return (
            (
                await session.execute(
                    select(User).where(User.phone_number == phone_number)
                )
            )
            .scalars()
            .first()
        )


user_crud = CRUDUser(User)
