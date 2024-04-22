from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.user import user_crud
from app.crud.base import CRUDBase
from app.crud.history import cars_history_crud
from app.models import Car


class CRUDCars(CRUDBase):

    async def update(
        self, user_id, object: Car, new_data, session: AsyncSession
    ):
        old_object_data = object.__repr__()
        update_data = new_data.dict(exclude_unset=True)
        user = await user_crud.get_user_by_telegram_id(user_id, session)

        for field in jsonable_encoder(object):
            if field in update_data:
                setattr(object, field, update_data[field])
        await cars_history_crud.create(
            user.id,
            object.id,
            old_object_data,
            object.__repr__(),
            session
        )
        session.add(object)
        await session.commit()
        await session.refresh(object)
        return object

    async def get_car_as_admin(self, object_id: int, session: AsyncSession):
        car = (
            (
                await session.execute(
                    select(self.model)
                    .where(self.model.id == object_id)
                    .options(selectinload(self.model.changes))
                )
            )
            .scalars()
            .first()
        )
        car.changes.sort(key=lambda x: x.date, reverse=True)
        return car

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
