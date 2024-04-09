from app.crud.base import CRUDBase
from app.models import LoyalitySettings
from sqlalchemy.ext.asyncio import AsyncSession


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


loyality_settings_crud = CRUDLoyalitySettings(LoyalitySettings)
