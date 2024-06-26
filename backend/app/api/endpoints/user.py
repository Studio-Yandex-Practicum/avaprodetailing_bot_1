from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    api_check_birth_date_less_current_data,
    api_check_phone_duplicate,
    api_check_telegram_id_duplicate,
    api_validate_and_format_phone_number,
    check_admin_user,
    check_birth_date_less_current_data,
    check_phone_dublicate,
    check_telegram_id_dublicate,
    check_user_exists,
    check_user_exists_by_phone_number,
    check_user_is_superuser,
    check_user_registered,
    valid_phone_number,
    check_mobile_phone_nuber_is_exists,
)
from app.core.db import get_async_session
from app.crud.user import user_crud
from app.crud.loyality import loyality_crud
from app.schemas.loyality import Loyality
from app.schemas.user import (
    CheckedUser,
    UserByAdmin,
    UserCreate,
    UserDBAdmin,
    UserFromDB,
    UserToAdmin,
    UserUpdate,
)
from app.models.loyality import LoyalityAction

router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/{telegram_id}', response_class=HTMLResponse)
async def get_registration_form(
    request: Request,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    context = {'request': request}
    user = await user_crud.get_user_by_telegram_id(telegram_id, session)
    if user:
        context['user'] = user
    return templates.TemplateResponse(
        'registration_form.html', context=context
    )


@router.get('/check_user/{telegram_id}', response_model=CheckedUser)
async def check_user(
    telegram_id: str, session: AsyncSession = Depends(get_async_session)
):
    await check_user_exists(telegram_id, session)
    return await user_crud.get_user_by_telegram_id(telegram_id, session)


@router.post('/')
async def process_registration(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    form_data: UserCreate = Depends(UserCreate.as_form),
):
    context = {'request': request, 'form': form_data, 'errors': []}
    try:
        await check_user_registered(form_data.telegram_id, session)
        form_data.phone_number = valid_phone_number(form_data.phone_number)
        await check_telegram_id_dublicate(None, form_data.telegram_id, session)
        await check_phone_dublicate(
            form_data.phone_number, form_data.telegram_id, session
        )
        check_birth_date_less_current_data(form_data.birth_date)
        await user_crud.create(form_data, session)
        user_id = (
            await user_crud.get_user_by_telegram_id(
                form_data.telegram_id,
                session
            )
        ).id
        await loyality_crud.create(
            admin_id=0,
            user_id=user_id,
            data=Loyality(
                action=LoyalityAction.charge,
                amount=100,
                user_id=user_id
            ),
            session=session
        )
        status_code = HTTPStatus.CREATED
    except ValueError as error:
        context['errors'].append(str(error))
        status_code = HTTPStatus.BAD_REQUEST
    return templates.TemplateResponse(
        'registration_form.html', context=context, status_code=status_code
    )


@router.get('/{telegram_id}/patch/{phone_number}')
async def get_update_form(
    request: Request,
    telegram_id: str,
    phone_number: str,
    session: AsyncSession = Depends(get_async_session),
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
    return templates.TemplateResponse('update_user.html', context=context)


@router.patch('/update/{user_id}')
async def user_update(
    request: Request,
    user_id: str,
    form_data: UserUpdate = Depends(UserUpdate.as_form),
    session: AsyncSession = Depends(get_async_session),
):
    errors = []
    try:
        await check_user_exists(user_id, session)
        user = await user_crud.get_user_by_telegram_id(user_id, session)
        form_data.phone_number = valid_phone_number(form_data.phone_number)
        await check_telegram_id_dublicate(
            form_data.telegram_id, user_id, session
        )
        await check_phone_dublicate(
            form_data.phone_number, form_data.telegram_id, session
        )
        check_birth_date_less_current_data(form_data.birth_date)
        await user_crud.update(user.id, user, form_data, session)
    except (HTTPException, ValueError) as error:
        errors.append(str(error))
    if errors:
        return templates.TemplateResponse(
            'update_user.html',
            {'request': request, 'user': form_data, 'errors': errors},
        )
    return templates.TemplateResponse(
        'user_updated.html', {'request': request}
    )


"""ADMIN ONLY API"""


@router.get('/admin/{telegram_id}', response_model=list[UserFromDB])
async def get_all_users_as_admin(
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    return await user_crud.get_all(session)


@router.get(
    '/admin/{telegram_id}/get_user/{user_id}', response_model=UserDBAdmin
)
async def get_user_as_admin(
    telegram_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_user_exists(user_id, session)
    return await user_crud.get_user_by_telegram_id_as_admin(user_id, session)


@router.patch('/admin/{telegram_id}/edit_user', response_model=UserFromDB)
async def edit_user_as_admin(
    telegram_id: str,
    update_data: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_user_exists(update_data.telegram_id, session)
    update_data.phone_number = api_validate_and_format_phone_number(
        update_data.phone_number
    )
    await api_check_telegram_id_duplicate(
        update_data.telegram_id, update_data.telegram_id, session
    )
    await api_check_phone_duplicate(
        update_data.phone_number, update_data.telegram_id, session
    )
    api_check_birth_date_less_current_data(update_data.birth_date)
    return await user_crud.update(
        telegram_id,
        await user_crud.get_user_by_telegram_id_as_admin(
            update_data.telegram_id, session
        ),
        update_data,
        session,
    )


@router.delete(
    '/admin/{telegram_id}/delete_user/{user_id}', response_model=UserFromDB
)
async def delete_user_as_admin(
    telegram_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_user_exists(user_id, session)
    return await user_crud.remove(
        await user_crud.get_user_by_telegram_id(user_id, session), session
    )


@router.get('/admin/{telegram_id}/add_user')
async def add_user_as_admin_form(
    telegram_id: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    return templates.TemplateResponse('add_user.html', dict(request=request))


@router.post('/admin/{telegram_id}/add_user')
async def add_user_as_admin(
    telegram_id: str,
    user_data: UserByAdmin,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_mobile_phone_nuber_is_exists(user_data.phone_number, session)
    return await user_crud.create(user_data, session)


@router.get('/admin/{telegram_id}/user_info')
async def get_user_info_as_admin(
    telegram_id: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    return templates.TemplateResponse(
        'get_edit_user.html', dict(request=request)
    )


@router.get('/admin/{telegram_id}/user_data/{user_phone_number}')
async def get_user_data_as_admin_by_telegram_id(
    telegram_id: str,
    user_phone_number: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    await check_user_exists_by_phone_number(user_phone_number, session)
    return await user_crud.get_user_by_phone_number(user_phone_number, session)


@router.get('/admin/{telegram_id}/search_user')
async def search_user(
    telegram_id: str,
    user: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_async_session),
):
    await check_admin_user(telegram_id, session)
    return await user_crud.get_user_by_substring_phone_number(user, session)


@router.get('/superuser/{telegram_id}/hire_admin')
async def get_hire_admin_form(
    request: Request,
    telegram_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_exists(telegram_id, session)
    await check_user_is_superuser(telegram_id, session)
    context = {'request': request}
    context['superuser_telegram_id'] = telegram_id
    return templates.TemplateResponse(
        'hire_admin_form.html', context, status_code=HTTPStatus.OK
    )


@router.patch(
    '/superuser/{telegram_id}/hire_admin', response_model=CheckedUser
)
async def hire_admin(
    telegram_id: str,
    data: UserToAdmin,
    session: AsyncSession = Depends(get_async_session),
):
    await check_user_exists(telegram_id, session)
    await check_user_is_superuser(telegram_id, session)
    await check_user_exists_by_phone_number(data.phone_number, session)
    return await user_crud.update(
        telegram_id,
        await user_crud.get_user_by_phone_number(data.phone_number, session),
        data,
        session,
    )
