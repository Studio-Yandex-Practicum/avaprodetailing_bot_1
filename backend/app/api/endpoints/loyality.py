from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.loyality import LoyalitySettings
from app.core.db import get_async_session
from app.crud.loyality import loyality_settings_crud
from app.api.validators import (
    check_user_exists,
    check_user_is_admin_or_superuser
)
from app.core.config import ID_LOYALITY_SETTINGS

router = APIRouter()


@router.get('/admin/{telegram_id}/', response_model=LoyalitySettings)
async def get_loyality_settings(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    await check_user_is_admin_or_superuser(telegram_id, session)
    if not await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session):
        await loyality_settings_crud.create(ID_LOYALITY_SETTINGS, session)
    return await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session)


@router.patch('/admin/{telegram_id}/', response_model=LoyalitySettings)
async def update_loyality_settings(
    telegram_id: str,
    update_data: LoyalitySettings,
    session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    await check_user_is_admin_or_superuser(telegram_id, session)
    return await loyality_settings_crud.update(
        await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session),
        update_data,
        session
    )
