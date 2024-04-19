from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.crud.history import user_history_crud
from app.models import User


class CRUDUser(CRUDBase):

    async def update(
        self, user_id, object: User, new_data, session: AsyncSession
    ):
        old_object_data = object.__repr__()
        update_data = new_data.dict(exclude_unset=True)
        for field in jsonable_encoder(object):
            if field in update_data:
                setattr(object, field, update_data[field])
        await user_history_crud.create(
            user_id, object.id, old_object_data, object.__repr__(), session
        )
        session.add(object)
        await session.commit()
        await session.refresh(object)
        return object

    async def get_user_by_telegram_id(
        self, telegram_id: str, session: AsyncSession
    ):
        return (
            (
                await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
            )
            .scalars()
            .first()
        )

    async def get_user_by_telegram_id_as_admin(
        self, telegram_id: int, session: AsyncSession
    ):
        user = (
            (
                await session.execute(
                    select(self.model)
                    .where(self.model.telegram_id == telegram_id)
                    .options(
                        selectinload(self.model.loyality),
                        selectinload(self.model.cars),
                        selectinload(self.model.payments),
                        selectinload(self.model.changes),
                    )
                )
            )
            .scalars()
            .first()
        )
        user.loyality_balance = sum(
            [loyality.amount for loyality in user.loyality]
        )
        user.changes.sort(key=lambda x: x.date, reverse=True)
        user.loyality.sort(key=lambda x: x.exp_date, reverse=True)
        user.payments.sort(key=lambda x: x.date, reverse=True)
        return user

    async def get_all_users_as_admin(
        self, session: AsyncSession
    ):
        user = (
            (
                await session.execute(
                    select(self.model)
                    .where(self.model.telegram_id != None)
                    .options(
                        selectinload(self.model.loyality),
                        selectinload(self.model.cars),
                        selectinload(self.model.payments),
                        selectinload(self.model.changes),
                    )
                )
            )
            .scalars()
            .all()
        )
        for i in user:
            i.loyality_balance = sum(
                [loyality.amount for loyality in i.loyality]
            )
        return user

    async def get_user_by_phone_number(
        self, phone_number: str, session: AsyncSession
    ) -> Optional[User]:
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
