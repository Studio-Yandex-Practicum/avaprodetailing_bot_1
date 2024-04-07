from http import HTTPStatus
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserUpdate, UserFromDB
from app.core.db import get_async_session
from app.crud.user import user_crud
from app.api.validators import (valid_phone_number,
                                check_phone_dublicate,
                                check_birth_date_less_current_data,
                                check_telegram_id_dublicate,
                                check_user_exists,
                                check_user_is_admin_or_superuser
                                )

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/{telegram_id}", response_class=HTMLResponse)
async def get_registration_form(
    request: Request,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    context = {'request': request}
    user = await user_crud.get_user_by_telegram_id(telegram_id, session)
    if user:
        context['user'] = user
    return templates.TemplateResponse(
        "registration_form.html",
        context=context
    )


@router.post("/")
async def process_registration(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    form_data: UserCreate = Depends(UserCreate.as_form),
) -> RedirectResponse:
    context = {
        'request': request,
        'form': form_data,
        'errors': []
    }
    try:
        form_data.phone_number = valid_phone_number(form_data.phone_number)
        await check_telegram_id_dublicate(None, form_data.telegram_id, session)
        await check_phone_dublicate(
            form_data.phone_number,
            form_data.telegram_id,
            session
        )
        check_birth_date_less_current_data(form_data.birth_date)
        await user_crud.create(form_data, session)
        status_code = HTTPStatus.CREATED
    except ValueError as error:
        context['errors'].append(str(error))
        status_code = HTTPStatus.BAD_REQUEST
    return templates.TemplateResponse(
        'registration_form.html',
        context=context,
        status_code=status_code
    )


@router.get('/{telegram_id}/patch/{phone_number}')
async def get_update_form(
    request: Request,
    telegram_id: str,
    phone_number: str,
    session: AsyncSession = Depends(get_async_session)
):
    context = {
        'request': request,
    }
    update_user = await user_crud.get_user_by_phone_number(
        phone_number, session
    )
    current_user = await user_crud.get_user_by_telegram_id(
        telegram_id, session
    )
    if not current_user or not update_user:
        return templates.TemplateResponse('404.html', context=context)
    if current_user.is_admin:
        context['admin'] = current_user.is_admin
        context['user'] = update_user
    if current_user.id == update_user.id:
        context['user'] = update_user
    context['user_id'] = update_user.telegram_id
    return templates.TemplateResponse(
        'update_user.html',
        context=context
    )


@router.post('/update/{user_id}')
async def user_update(
    request: Request,
    user_id: str,
    form_data: UserUpdate = Depends(UserUpdate.as_form),
    session: AsyncSession = Depends(get_async_session),
):
    errors = []
    try:
        user = await user_crud.get_user_by_telegram_id(user_id, session)
        form_data.phone_number = valid_phone_number(form_data.phone_number)
        await check_telegram_id_dublicate(
            form_data.telegram_id,
            user_id,
            session
        )
        await check_phone_dublicate(
            form_data.phone_number,
            form_data.telegram_id,
            session
        )

        check_birth_date_less_current_data(form_data.birth_date)
        await user_crud.update(user, form_data, session)
    except (HTTPException, ValueError) as error:
        errors.append(str(error))
    if errors:
        return templates.TemplateResponse(
            "update_user.html", {
                'request': request,
                'user': form_data,
                'errors': errors
            }
        )
    return templates.TemplateResponse(
        'user_updated.html',
        {
            'request': request
        }
    )


@router.delete(
        'admin/{telegram_id}/delete_user/{user_id}',
        response_model=UserFromDB
)
async def user_remove_admin(
    telegram_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_exists(telegram_id, session)
    await check_user_exists(user_id, session)
    await check_user_is_admin_or_superuser(telegram_id, session)
    user = user_crud.get_user_by_telegram_id(user_id, session)
    return await user_crud.remove(user, session)
