from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from app.core.db import get_async_session
from app.crud.user import user_crud

router = APIRouter()


@router.get('/check_user/{telegram_id}')
async def check_user(
    telegram_id: str, session: AsyncSession = Depends(get_async_session)
):
    return await user_crud.get_user_by_telegram_id(telegram_id, session)
