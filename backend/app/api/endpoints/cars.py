from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_car_before_edit,
    check_car_data_before_create,
    check_car_exists,
    check_user_before_car_delete,
    check_user_is_admin_or_superuser,
)
from app.core.db import get_async_session
from app.crud.cars import cars_crud
from app.schemas.cars import CarCreate, CarDB, CarDBAdmin, CarUpdate

router = APIRouter()


@router.get('/{telegram_id}/', response_model=list[CarDBAdmin])
async def get_all_cars_as_admin(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_is_admin_or_superuser(telegram_id, session)
    return await cars_crud.get_all(session)


@router.get('/{telegram_id}/my_cars', response_model=list[CarDB])
async def get_my_cars(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await cars_crud.get_my_cars(telegram_id, session)


@router.post('/{telegram_id}/add_car', response_model=CarDB)
async def add_car(
    car: CarCreate,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_car_data_before_create(telegram_id, car, session)
    return await cars_crud.create(
        car,
        session=session,
    )


@router.patch('/{telegram_id}/edit_car/{car_id}', response_model=CarDB)
async def edit_car(
    car_id: int,
    update_data: CarUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    await check_car_exists(car_id, session)
    await check_car_before_edit(
        car_id,
        update_data,
        session=session,
    )
    return await cars_crud.update(
        await cars_crud.get(car_id, session),
        new_data=await check_car_before_edit(
            car_id,
            update_data,
            session,
        ),
        session=session,
    )


@router.delete('/{telegram_id}/delete_car/{car_id}', response_model=CarDB)
async def delete_car(
    telegram_id: str,
    car_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    await check_car_exists(car_id, session)
    car = await cars_crud.get(car_id, session)
    await check_user_before_car_delete(car, telegram_id, session)
    return await cars_crud.remove(
        car,
        session,
    )
