from app.crud.base import CRUDBase
from app.crud.user import user_crud
from app.models import LoyalitySettings, Loyality
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select


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


class CRUDLoyality(CRUDBase):
    async def get_count_of_points(
        self,
        telegram_id: str,
        session: AsyncSession
    ):
        return (
            await session.execute(
                select(
                    func.sum(Loyality.amount)
                ).filter(
                    Loyality.user_id == (
                        await user_crud.get_user_by_telegram_id(
                            telegram_id,
                            session
                        )
                    ).id
                )
            )
        ).scalars().first()

    async def get_list_of_transactions(
        self,
        telegram_id: str,
        session: AsyncSession
    ):
        return (await session.execute(
            select(Loyality).filter(
                Loyality.user_id == (
                    await user_crud.get_user_by_telegram_id(
                        telegram_id,
                        session
                    )
                ).id
            )
        )).scalars().all()


loyality_settings_crud = CRUDLoyalitySettings(LoyalitySettings)
loyality_crud = CRUDLoyality(Loyality)
