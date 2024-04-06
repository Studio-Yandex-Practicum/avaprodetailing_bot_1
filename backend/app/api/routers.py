from fastapi import APIRouter

from .endpoints.user import user_router

main_router = APIRouter()

main_router.include_router(user_router)
