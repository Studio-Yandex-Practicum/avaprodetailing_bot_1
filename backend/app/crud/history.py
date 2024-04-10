from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import History

COMMENT = (
    'User id:{user.id} name: {user.last_name} {user.first_name} '
    'changed {model} from {old_value} to '
    '{new_value}'
)


class CRUDHistory(CRUDBase):
    async def create(
        self,
        user,
        model: str,
        old_value: any,
        new_value: any,
        session: AsyncSession
    ) -> History:
        obj = self.model(
            user=user.id,
            table=model,
            comment=COMMENT.format(
                user.id,
                user.last_name,
                user.first_name,
                model,
                old_value,
                new_value
            )
        )
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


history_crud = CRUDHistory(History)
