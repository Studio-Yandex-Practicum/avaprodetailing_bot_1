from fastapi import APIRouter

from app.api.endpoints import cars_router, users_router

CARS_PREFIX = '/cars'
USERS_PREFIX = '/users'

main_router = APIRouter()
main_router.include_router(
    cars_router, prefix=CARS_PREFIX, tags=['Автомобили']
)
main_router.include_router(
    users_router, prefix=USERS_PREFIX, tags=['Пользователи']
)
