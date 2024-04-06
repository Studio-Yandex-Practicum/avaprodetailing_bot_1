from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserUpdate
from app.core.db import get_async_session
from app.crud.user import user_crud
from app.api.validators import (valid_phone_number,
                                check_phone_dublicate,
                                check_birth_date_less_current_data,
                                check_telegram_id_dublicate)

user_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@user_router.get("/user/{id}/", response_class=HTMLResponse)
async def get_registration_form(
    request: Request,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    user = await user_crud.get_user_by_telegram_id(telegram_id, session)
    if user:
        return templates.TemplateResponse("registration_form.html", {"request": request, 'user': user})
    return templates.TemplateResponse("registration_form.html", {"request": request})


@user_router.post("/user/{id}")
async def process_registration(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    form_data: UserCreate = Depends(UserCreate.as_form),
) -> RedirectResponse:
    errors = []
    try:
        form_data.phone_number = valid_phone_number(form_data.phone_number)
        await check_telegram_id_dublicate(form_data.telegram_id, session)
        await check_phone_dublicate(
            form_data.phone_number,
            form_data.telegram_id,
            session
        )
        check_birth_date_less_current_data(form_data.birth_date)
        await user_crud.create_user(form_data, session)
    except ValueError as error:
        errors.append(str(error))
    if errors:
        return templates.TemplateResponse(
            "registration_form.html", {
                'request': request,
                'form': form_data,
                'errors': errors
            }
        )
    return templates.TemplateResponse(
        'user_created.html',
        {
            "request": request,
            'form': form_data
        }
    )

@user_router.get('/user/{telegram_id}/patch/{phone_number}')
async def get_update_form(
    request: Request,
    telegram_id: str,
    phone_number: str,
    session: AsyncSession = Depends(get_async_session)
):
    context = {'request': request}
    update_user = await user_crud.get_user_by_phone_number(
        phone_number, session
    )
    current_user = await user_crud.get_user_by_telegram_id(
        telegram_id, session
    )
    print(update_user, 'updaaaaaaaaaaaaate')
    print(current_user, 'ccccccccccc')
    if not current_user:
        return templates.TemplateResponse('404.html', context=context)
    if current_user.is_admin:
        context['admin'] = current_user.is_admin
        context['user'] = update_user
    if current_user.id == update_user.id:
        context['user'] = update_user
    return templates.TemplateResponse(
        'update_user.html',
        context=context
    )


@user_router.patch('/user/{id}')
async def user_update(
    request: Request,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
    form_data: UserUpdate = Depends(UserUpdate.as_form)
) -> UserUpdate:
    errors = []
    try:
        user = await user_crud.get_user_by_telegram_id(telegram_id, session)
        form_data.phone_number = valid_phone_number(form_data.phone_number)
        await check_telegram_id_dublicate(form_data.telegram_id, session)
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
            "registration_form.html", {
                'request': request,
                'form': form_data,
                'errors': errors
            }
        )
    return templates.TemplateResponse('user_created.html', {'request': request})


@user_router.delete('admin/{telegram_id}/delete_user/{phone_number}')
async def user_remove_admin(
    telegram_id: str,
    phone_number: str,
    session:AsyncSession = Depends(get_async_session),
):
    pass