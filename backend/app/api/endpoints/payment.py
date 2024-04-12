import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_admin_user,
    check_user_exists,
    check_user_is_admin_or_superuser,
)
from app.core.db import get_async_session
from app.crud.payment import payments_crud
from app.crud.user import user_crud
from app.schemas.payment import (
    PaymentCreate,
    PaymentCreateAdmin,
    PaymentDBAdmin,
    PaymentUpdate,
)

router = APIRouter()


"""ADMIN ONLY"""


@router.get(
    '/admin/{admin_telegram_id}',
    response_model=list[PaymentDBAdmin],
)
async def get_all_payments(
    admin_telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    return await payments_crud.get_all(session)


@router.get(
    '/admin/{admin_telegram_id}/payment/{generate_payment_id}',
    response_model=PaymentDBAdmin,
)
async def get_payment(
    admin_telegram_id: str,
    generate_payment_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    return await payments_crud.get_payment_by_uuid(
        generate_payment_id, session
    )


@router.post(
    '/admin/{admin_telegram_id}/create_payment/{user_telegram_id}',
    response_model=PaymentDBAdmin,
)
async def add_payment(
    payment: PaymentCreateAdmin,
    admin_telegram_id: str,
    user_telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    await check_user_exists(user_telegram_id, session)
    return await payments_crud.create(
        PaymentCreate(
            admin_id=(
                await user_crud.get_user_by_telegram_id(
                    admin_telegram_id, session
                )
            ).id,
            payer_id=(
                await user_crud.get_user_by_telegram_id(
                    user_telegram_id, session
                )
            ).id,
            price=payment.price,
            payment_method=payment.payment_method,
            generated_payment_id=uuid.uuid4().__str__(),
        ),
        session,
    )


@router.patch(
    '/admin/{admin_telegram_id}/edit_payment/{generate_payment_id}',
    response_model=PaymentDBAdmin,
)
async def set_payment_is_paid(
    update_data: PaymentUpdate,
    admin_telegram_id: str,
    generate_payment_id,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    return await payments_crud.update(
        await payments_crud.get_payment_by_uuid(generate_payment_id, session),
        update_data,
        session,
    )
