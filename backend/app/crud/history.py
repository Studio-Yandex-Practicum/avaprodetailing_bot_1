from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import History


class CRUDHistory(CRUDBase):
    async def create(
        self,
        user,
        model: str,
        old_value: any,
        new_value: any,
        session: AsyncSession
    ) -> History:
        comment = (
            f'User id:{user.id} name: {user.last_name} {user.first_name} '
            f'changed {model} from {old_value} to '
            f'{new_value}')
        obj = self.model(user=user.id, table=model, comment=comment)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


history_crud = CRUDHistory(History)
                