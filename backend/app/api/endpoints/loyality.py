from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_admin_user,
    check_user_exists,
    check_user_is_admin_or_superuser
)
from app.core.config import ID_LOYALITY_SETTINGS
from app.core.db import get_async_session
from app.core.descriptions import (
    DECRIPTION_GET_LOYALITY_HISTORY,
    DESCRIPTION_GET_LOYALITY_POINT
)
from app.crud.history import history_crud
from app.crud.loyality import loyality_crud, loyality_settings_crud
from app.crud.user import user_crud
from app.schemas.loyality import Loyality, LoyalityList, LoyalitySettings


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
    await history_crud.create(
        await user_crud.get_user_by_telegram_id(telegram_id, session),
        loyality_settings_crud.model.__name__,
        await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session),
        update_data,
        session)
    return await loyality_settings_crud.update(
        await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session),
        update_data,
        session
    )


@router.get('/user/{telegram_id}/', description=DESCRIPTION_GET_LOYALITY_POINT)
async def get_loyality_points(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    return [
        dict(
            count=await loyality_crud.get_count_of_points(telegram_id, session)
        )
    ]


@router.get(
    '/user/{telegram_id}/history',
    description=DECRIPTION_GET_LOYALITY_HISTORY
)
async def get_loyality_history(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    return await loyality_crud.get_list_of_transactions(telegram_id, session)


@router.post(
    '/admin/{telegram_id}/history/{user_telegram_id}/',
    response_model=LoyalityList
)
async def add_loyality_history(
    telegram_id: str,
    user_telegram_id: str,
    data: Loyality,
    session: AsyncSession = Depends(get_async_session)
):
    await check_admin_user(telegram_id, session)
    await check_user_exists(user_telegram_id, session)
    return await loyality_crud.create(
        data,
        session=session,
    )
