from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import (
    CarHistory,
    LoyalityHistory,
    LoyalitySettingsHistory,
    UserHistory,
)


class CRUDHistory(CRUDBase):

    async def create(
        self,
        user_id: int,
        object_id: int,
        old_data: any,
        new_data: any,
        session: AsyncSession,
    ):
        obj = self.model(
            changed_by_id=user_id,
            object_id=object_id,
            old_data=old_data,
            new_data=new_data,
        )
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


class CRUDLoyalityHistory(CRUDBase):

    async def create(
        self,
        admin_id,
        user_id,
        loyality_id,
        new_data,
        session: AsyncSession,
    ):
        new_object = self.model(
            admin_id=admin_id,
            user_id=user_id,
            loyality_id=loyality_id,
            new_data=new_data,
        )
        session.add(new_object)
        await session.commit()
        await session.refresh(new_object)
        return new_object


cars_history_crud = CRUDHistory(CarHistory)
loyality_history_crud = CRUDLoyalityHistory(LoyalityHistory)
loyality_settings_history_crud = CRUDHistory(LoyalitySettingsHistory)
user_history_crud = CRUDHistory(UserHistory)
