# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.schemas.loyality import LoyalitySettings
# from app.core.db import get_async_session
# from app.crud.loyality import loyality_settings_crud

# router = APIRouter()


# @router.get('admin/{telegram_id}/', response_model=LoyalitySettings)
# async def get_loyality_settings(
#     telegram_id: str,
#     session: AsyncSession = Depends(get_async_session)
# ):
#     return await loyality_settings_crud(session)
