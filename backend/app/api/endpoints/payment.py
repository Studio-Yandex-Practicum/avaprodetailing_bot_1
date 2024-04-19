from http import HTTPStatus
from uuid import uuid4


from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import cash_payment_background_tasks
from app.api.validators import (
    check_admin_user,
    check_user_exists_by_phone_number,
)
from app.core.db import get_async_session
from app.crud.payment import payments_crud
from app.crud.user import user_crud
from app.schemas.payment import (
    PaymentCashCreate,
    PaymentCreate,
    PaymentCreateLoyality,
    PaymentDBAdmin,
)
from app.services.utils import payment_background_tasks


router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


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
    '/admin/{admin_telegram_id}/create_payment', response_model=PaymentDBAdmin
)
async def add_payment(
    payment: PaymentCreateLoyality,
    admin_telegram_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    await check_user_exists_by_phone_number(payment.payer_id, session)
    admin_id = (
        await user_crud.get_user_by_telegram_id(admin_telegram_id, session)
    ).id
    client = await user_crud.get_user_by_phone_number(
        payment.payer_id, session
    )
    payer_id, payer_telegram_id = client.id, client.telegram_id
    loyality_action = payment.action
    loyality_amount = payment.loyality_points
    price = payment.price
    if loyality_action == 'списано':
        price = price - loyality_amount
        loyality_amount = -(loyality_amount)
    match payment.payment_method:
        case 'cash':
            new_payment = await payments_crud.create(
                PaymentCashCreate(
                    admin_id=admin_id,
                    payer_id=payer_id,
                    price=price,
                    payment_method=payment.payment_method,
                    is_paid=True,
                    generated_payment_id=uuid4().__str__(),
                ),
                session,
            )
            background_tasks.add_task(
                cash_payment_background_tasks,
                admin_telegram_id,
                admin_id,
                payer_telegram_id,
                payer_id,
                loyality_action,
                loyality_amount,
                new_payment.id,
                price,
                session,
            )
        case 'online':
            new_payment = await payments_crud.create(
                PaymentCreate(
                    admin_id=admin_id,
                    payer_id=payer_id,
                    price=price,
                    payment_method=payment.payment_method,
                ),
                session,
            )
            background_tasks.add_task(
                payment_background_tasks,
                admin_telegram_id,
                new_payment,
                payer_telegram_id,
                admin_id,
                payer_id,
                loyality_action,
                loyality_amount,
                session,
            )
    return new_payment


"""FRONTEND"""


@router.get('/admin/{admin_telegram_id}/create_payment')
async def create_payment_form(
    request: Request,
    admin_telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(admin_telegram_id, session)
    context = {'request': request}
    context['admin_telegram_id'] = admin_telegram_id
    return templates.TemplateResponse(
        'payment_form.html', context, status_code=HTTPStatus.OK
    )
