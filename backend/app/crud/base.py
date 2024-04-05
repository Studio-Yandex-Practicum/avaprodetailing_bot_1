from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Car


class CRUDBase:

    def __init__(self, model):
        self.model: Car = model

    async def get(self, object_id: int, session: AsyncSession):
        return (
            (
                await session.execute(
                    select(self.model).where(self.model.id == object_id)
                )
            )
            .scalars()
            .first()
        )

    async def get_all(self, session: AsyncSession):
        return (
            (await session.execute(select(self.model).order_by(self.model.id)))
            .scalars()
            .all()
        )

    async def create(
        self,
        data,
        session: AsyncSession,
    ):
        new_object_data = data.dict()
        new_object = self.model(**new_object_data)
        session.add(new_object)
        await session.commit()
        await session.refresh(new_object)
        return new_object

    async def update(self, object, new_data, session: AsyncSession):
        update_data = new_data.dict(exclude_unset=True)
        for field in jsonable_encoder(object):
            if field in update_data:
                setattr(object, field, update_data[field])
        session.add(object)
        await session.commit()
        await session.refresh(object)
        return object

    async def remove(self, object, session: AsyncSession):
        await session.delete(object)
        await session.commit()
        return object
