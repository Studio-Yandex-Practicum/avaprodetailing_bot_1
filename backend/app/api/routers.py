from app.api.endpoints import cars_router
from fastapi import APIRouter

CARS_PREFIX = '/cars'

main_router = APIRouter()
main_router.include_router(
    cars_router, prefix=CARS_PREFIX, tags=['Автомобили']
)
