from fastapi import APIRouter

from app.api.endpoints import (
    cars_router,
    loyality_router,
    payments_router,
    users_router,
)

CARS_PREFIX = '/cars'
USERS_PREFIX = '/users'
LOYALITY_PREFIX = '/loyality'
PAYMENTS_PREFIX = '/payments'

main_router = APIRouter()
main_router.include_router(
    cars_router, prefix=CARS_PREFIX, tags=['Автомобили']
)
main_router.include_router(
    users_router, prefix=USERS_PREFIX, tags=['Пользователи']
)
main_router.include_router(
    loyality_router, prefix=LOYALITY_PREFIX, tags=['Баллы лояльности']
)
main_router.include_router(
    payments_router, prefix=PAYMENTS_PREFIX, tags=['Платежи']
)
