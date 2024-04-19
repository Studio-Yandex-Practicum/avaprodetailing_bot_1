from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_admin_user,
    check_car_before_edit,
    check_car_data_before_create,
    check_car_exists,
    check_length_user_car_list,
    check_user_exists,
    check_user_is_owner,
)
from app.core.db import get_async_session
from app.crud.cars import cars_crud
from app.schemas.cars import (
    CarCreate,
    CarCreateUser,
    CarDB,
    CarDBAdmin,
    CarListDBAdmin,
    CarUpdate,
    CarListUser
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

"""ADMIN OR SUPERUSER ROLE"""


@router.get('/admin/{telegram_id}/', response_model=list[CarListDBAdmin])
async def get_all_cars_as_admin(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    return await cars_crud.get_all(session)


@router.get('/admin/{telegram_id}/get_car/{car_id}', response_model=CarDBAdmin)
async def get_car(
    car_id: int,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_car_exists(car_id, session)
    return await cars_crud.get_car_as_admin(car_id, session)


@router.post('/admin/{telegram_id}/add_car', response_model=CarDBAdmin)
async def add_car_as_admin(
    car_data: CarCreate,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_user_exists(car_data.owner_telegram_id, session)
    await check_car_data_before_create(car_data, session)
    return await cars_crud.get_car_as_admin(
        (
            await cars_crud.create(
                car_data,
                session=session,
            )
        ).id,
        session,
    )


@router.patch(
    '/admin/{telegram_id}/edit_car/{car_id}', response_model=CarDBAdmin
)
async def edit_car_as_admin(
    car_id: int,
    telegram_id: str,
    update_data: CarUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_car_exists(car_id, session)
    await check_car_before_edit(
        car_id,
        update_data,
        session=session,
    )
    await cars_crud.update(
        telegram_id,
        await cars_crud.get(car_id, session),
        update_data,
        session=session,
    )
    return await cars_crud.get_car_as_admin(car_id, session)


@router.delete(
    '/admin/{telegram_id}/delete_car/{car_id}', response_model=CarDBAdmin
)
async def delete_car_as_admin(
    telegram_id: str,
    car_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_car_exists(car_id, session)
    return await cars_crud.remove(
        await cars_crud.get_car_as_admin(car_id, session),
        session,
    )


"""USER ROLE"""


@router.get('/{telegram_id}', response_model=list[CarListUser])
async def get_my_cars(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_exists(telegram_id, session)
    return await cars_crud.get_my_cars(telegram_id, session)


@router.post('/{telegram_id}/add_car', response_model=CarDB)
async def add_car(
    #car_data: CarCreateUser,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
    car_data: CarCreateUser = Depends(CarCreateUser.as_form),

):
    await check_user_exists(telegram_id, session)
    await check_car_data_before_create(car_data, session)
    return await cars_crud.create(
        CarCreate(
            brand=car_data.brand,
            model=car_data.model,
            number_plate=car_data.number_plate,
            owner_telegram_id=telegram_id,
        ),
        session=session,
    )


@router.patch('/{telegram_id}/edit_car/{car_id}', response_model=CarDB)
async def edit_car(
    car_id: int,
    telegram_id: str,
    update_data: CarUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_exists(telegram_id, session)
    await check_car_exists(car_id, session)
    car = await cars_crud.get(car_id, session)
    await check_user_is_owner(car, telegram_id, session)
    await check_car_before_edit(
        car_id,
        update_data,
        session=session,
    )
    return await cars_crud.update(
        telegram_id,
        car,
        update_data,
        session=session,
    )


@router.delete('/{telegram_id}/delete_car/{car_id}', response_model=CarDB)
async def delete_car(
    telegram_id: str,
    car_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_exists(telegram_id, session)
    await check_car_exists(car_id, session)
    car = await cars_crud.get(car_id, session)
    await check_user_is_owner(car, telegram_id, session)
    await check_length_user_car_list(telegram_id, session)
    return await cars_crud.remove(
        car,
        session,
    )


@router.get('/{telegram_id}/add_car/add_form')
async def add_car_form(
    request: Request,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    context = {'request': request}
    context['telegram_id'] = telegram_id
    return templates.TemplateResponse(
        'car_form.html',
        context,
        status_code=HTTPStatus.OK
    )


@router.get('/{telegram_id}/edit_car/{car_id}/edit_form')
async def edit_car_form(
    request: Request,
    car_id: int,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    return templates.TemplateResponse(
        'car_form.html',
        dict(
            request=request,
            form_data=await cars_crud.get(car_id, session)
        ),
        status_code=HTTPStatus.OK
    )
