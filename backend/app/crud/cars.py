from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Car


class CRUDCars(CRUDBase):
    async def get_my_cars(self, telegram_id: str, session: AsyncSession):
        return (
            (
                await session.execute(
                    select(Car).where(Car.owner_telegram_id == telegram_id)
                )
            )
            .scalars()
            .all()
        )

    async def get_car_by_number(
        self, number_plate: str, session: AsyncSession
    ):
        return (
            (
                await session.execute(
                    select(Car).where(Car.number_plate == number_plate)
                )
            )
            .scalars()
            .first()
        )


cars_crud = CRUDCars(Car)
