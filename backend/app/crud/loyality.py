from datetime import datetime, timedelta

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import LIFETIME_OF_BONUSES_IN_DAYS
from app.crud.base import CRUDBase
from app.crud.history import (
    loyality_settings_history_crud,
)
from app.crud.history import loyality_history_crud
from app.models import Loyality, LoyalitySettings


class CRUDLoyalitySettings(CRUDBase):
    async def create(
        self,
        id: int,
        session: AsyncSession,
    ):
        new_object = self.model(id=id)
        session.add(new_object)
        await session.commit()
        await session.refresh(new_object)
        return new_object

    async def update(
        self,
        user_id: int,
        object: LoyalitySettings,
        new_data,
        session: AsyncSession,
    ):
        old_object_data = object.__repr__()
        update_data = new_data.dict(exclude_unset=True)
        for field in jsonable_encoder(object):
            if field in update_data:
                setattr(object, field, update_data[field])
        await loyality_settings_history_crud.create(
            user_id, object.id, old_object_data, object.__repr__(), session
        )
        session.add(object)
        await session.commit()
        await session.refresh(object)
        return object


class CRUDLoyality(CRUDBase):

    async def create(
        self,
        admin_id: int,
        user_id: int,
        data,
        session: AsyncSession,
    ):
        new_object_data = data.dict()
        new_object = self.model(
            **new_object_data,
            exp_date=datetime.now()
            + timedelta(days=LIFETIME_OF_BONUSES_IN_DAYS)
        )
        session.add(new_object)
        await session.commit()
        await session.refresh(new_object)
        await loyality_history_crud.create(
            admin_id, user_id, new_object.id, new_object.__repr__(), session
        )
        return new_object

    async def get_count_of_points(
        self, telegram_id: str, session: AsyncSession
    ):
        return (
            (
                await session.execute(
                    select(func.sum(Loyality.amount)).filter(
                        Loyality.user_id == telegram_id
                    )
                )
            )
            .scalars()
            .first()
        )

    async def get_list_of_transactions(
        self, telegram_id: str, session: AsyncSession
    ):
        return (
            (
                await session.execute(
                    select(Loyality).filter(Loyality.user_id == telegram_id)
                )
            )
            .scalars()
            .all()
        )


loyality_settings_crud = CRUDLoyalitySettings(LoyalitySettings)
loyality_crud = CRUDLoyality(Loyality)
