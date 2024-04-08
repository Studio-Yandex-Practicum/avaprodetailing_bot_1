from fastapi import APIRouter

from app.api.endpoints import cars_router, users_router# , loyality_router

CARS_PREFIX = '/cars'
USERS_PREFIX = '/users'
LOYALITY_PREFIX = '/loyality'

main_router = APIRouter()
main_router.include_router(
    cars_router, prefix=CARS_PREFIX, tags=['Автомобили']
)
main_router.include_router(
    users_router, prefix=USERS_PREFIX, tags=['Пользователи']
)
# main_router.include_router(
#     loyality_router, prefix=LOYALITY_PREFIX, tags=['Баллы лояльности']
# )
