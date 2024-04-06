from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

class UserCRUD:
    def __init__(self, model):
        self.model = model

    @staticmethod
    async def get_user_by_telegram_id(
            telegram_id: str,
            session: AsyncSession,
    ) -> User:
        user = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )
        return user.scalars().first()

    @staticmethod
    async def get_user_by_phone_number(
            phone_number: str,
            session: AsyncSession,
    ) -> Optional[str]:
        db_user_id = await session.execute(
            select(User).where(
                User.phone_number == phone_number
            )
        )
        return db_user_id.scalars().first()
    
    async def get_users(
        self,
        session: AsyncSession
    ) -> list[User]:
        all_users = await session.execute(
            select(self.model)
        )
        return all_users.scalars().all()

    async def create_user(
        self,
        obj_in,
        session: AsyncSession
    ) -> User:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj,
            obj_in,
            session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

user_crud = UserCRUD(User)
