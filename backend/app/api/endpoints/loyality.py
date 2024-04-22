from http import HTTPStatus

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import loyality_background_tasks
from app.api.validators import (
    check_admin_user,
    check_loyality_balance,
    check_user_exists,
    check_user_exists_by_phone_number,
)
from app.core.config import ID_LOYALITY_SETTINGS
from app.core.db import get_async_session
from app.core.descriptions import (
    DECRIPTION_GET_LOYALITY_HISTORY,
    DESCRIPTION_GET_LOYALITY_POINT,
)
from app.crud.loyality import loyality_crud, loyality_settings_crud
from app.crud.user import user_crud
from app.schemas.loyality import Loyality, LoyalitySettings


router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/admin/{telegram_id}/', response_model=LoyalitySettings)
async def get_loyality_settings(
    telegram_id: str, session: AsyncSession = Depends(get_async_session)
):
    await check_admin_user(telegram_id, session)
    obj = await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session)
    return (
        await loyality_settings_crud.create(ID_LOYALITY_SETTINGS, session)
        if not obj
        else obj
    )


@router.patch('/admin/{telegram_id}/', response_model=LoyalitySettings)
async def update_loyality_settings(
    telegram_id: str,
    update_data: LoyalitySettings,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    return await loyality_settings_crud.update(
        telegram_id,
        await loyality_settings_crud.get(ID_LOYALITY_SETTINGS, session),
        update_data,
        session,
    )


@router.get(
    '/admin/{admin_telegram_id}/{phone_number}/',
    description=DESCRIPTION_GET_LOYALITY_POINT,
)
async def get_loyality_points_as_admin_by_phone_number(
    admin_telegram_id,
    phone_number: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    await check_user_exists_by_phone_number(phone_number, session)
    return dict(
        count=await loyality_crud.get_count_of_points_by_phone_number(
            phone_number, session
        ),
    )


@router.get('/user/{telegram_id}/', description=DESCRIPTION_GET_LOYALITY_POINT)
async def get_loyality_points_by_telegram_id(
    telegram_id: str, session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    return dict(
        count=await loyality_crud.get_count_of_points(telegram_id, session),
    )


@router.get(
    '/user/{telegram_id}/history', description=DECRIPTION_GET_LOYALITY_HISTORY
)
async def get_loyality_history(
    telegram_id: str, session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    return await loyality_crud.get_list_of_transactions(telegram_id, session)


@router.post('/admin/{telegram_id}/')
async def add_loyality(
    telegram_id: str,
    data: Loyality,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    user = await user_crud.get_user_by_phone_number(data.user_id, session)
    user_id = user.id
    user_telegram_id = user.telegram_id
    await check_user_exists(user_telegram_id, session)
    await check_loyality_balance(data, user_telegram_id, session)
    if data.action == 'списание':
        data.amount = -(data.amount)
    background_tasks.add_task(
        loyality_background_tasks,
        telegram_id,
        user_telegram_id,
        data.user_id,
        data.action,
        data.amount,
    )
    return await loyality_crud.create(
        telegram_id,
        user_telegram_id,
        Loyality(
            action=data.action,
            amount=data.amount,
            user_id=user_id,
        ),
        session,
    )


"""FRONTEND"""


@router.get('/admin/{admin_telegram_id}/loyality_form')
async def add_loyality_form(
    request: Request,
    admin_telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    context = {'request': request}
    context['admin_telegram_id'] = admin_telegram_id
    return templates.TemplateResponse(
        'loyality_form.html', context, status_code=HTTPStatus.OK
    )
