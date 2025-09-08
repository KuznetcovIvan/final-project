from http import HTTPStatus  # noqa: I001

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import generate_invite_code, user_admin_or_superuser, user_member_or_superuser
from app.api.validators import (
    check_company_exists,
    check_department_in_company_exists,
    check_news_in_company_exists,
    check_invite_exists,
    check_before_invite,
)
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.company import company_crud, department_crud, invites_crud, membership_crud, news_crud
from app.models.company import UserRole
from app.models.user import User
from app.schemas.company import (
    CompanyCreate,
    CompanyMembershipCreate,
    CompanyMembershipRead,
    CompanyNewsCreate,
    CompanyNewsRead,
    CompanyNewsUpdate,
    CompanyRead,
    CompanyUpdate,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    InviteCreate,
    InviteRead,
)
from app.services.invite import send_invite_email

COMPANY_NAME_EXISTS = 'Компания с именем "{}" уже существует.'
DEPARTMENT_NAME_EXISTS = 'В компании id={} уже существует отдел "{}".'
MEMBERSHIP_EXISTS = 'Пользователь id={} уже состоит в компании id={}'

router = APIRouter(prefix='/companies')


@router.post('/', response_model=CompanyMembershipRead, response_model_exclude_none=True)
async def create_new_company(
    obj_in: CompanyCreate, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)
):
    try:
        company = await company_crud.create(obj_in, session, commit=False)
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=COMPANY_NAME_EXISTS.format(obj_in.name))
    membership = await membership_crud.create(
        CompanyMembershipCreate(user_id=user.id, company_id=company.id, role=UserRole.ADMIN),
        session=session,
        commit=False,
    )
    await session.commit()
    await session.refresh(membership)
    return membership


@router.get('/', response_model=list[CompanyRead], response_model_exclude_none=True)
async def get_all_companies(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)):
    return await company_crud.get_multi_by_user(user, session)


@router.patch(
    '/{company_id}',
    response_model=CompanyRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def update_company(company_id: int, obj_in: CompanyUpdate, session: AsyncSession = Depends(get_async_session)):
    try:
        company = await company_crud.update(await check_company_exists(company_id, session), obj_in, session)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=COMPANY_NAME_EXISTS.format(obj_in.name))
    return company


@router.delete(
    '/{company_id}',
    response_model=CompanyRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def remove_company(company_id: int, session: AsyncSession = Depends(get_async_session)):
    return await company_crud.remove(await check_company_exists(company_id, session), session)


@router.get(
    '/{company_id}/news',
    response_model=list[CompanyNewsRead],
    response_model_exclude_none=True,
    dependencies=[Depends(user_member_or_superuser)],
)
async def get_all_news(company_id: int, session: AsyncSession = Depends(get_async_session)):
    await check_company_exists(company_id, session)
    return await news_crud.get_multi_by_company(company_id, session)


@router.post('/{company_id}/news', response_model=CompanyNewsRead, response_model_exclude_none=True)
async def create_news(
    company_id: int,
    obj_in: CompanyNewsCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_admin_or_superuser),
):
    await check_company_exists(company_id, session)
    return await news_crud.create(obj_in, user, company_id, session)


@router.patch(
    '/{company_id}/news/{news_id}',
    response_model=CompanyNewsRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def update_news(
    news_id: int, company_id: int, obj_in: CompanyNewsUpdate, session: AsyncSession = Depends(get_async_session)
):
    news = await check_news_in_company_exists(news_id, company_id, session)
    return await news_crud.update(news, obj_in, session)


@router.delete(
    '/{company_id}/news/{news_id}',
    response_model=CompanyNewsRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def remove_news(news_id: int, company_id: int, session: AsyncSession = Depends(get_async_session)):
    news = await check_news_in_company_exists(news_id, company_id, session)
    return await news_crud.remove(news, session)


@router.get(
    '/{company_id}/departments',
    response_model=list[DepartmentRead],
    response_model_exclude_none=True,
    dependencies=[Depends(user_member_or_superuser)],
)
async def get_all_departments(company_id: int, session: AsyncSession = Depends(get_async_session)):
    await check_company_exists(company_id, session)
    return await department_crud.get_multi_by_company(company_id, session)


@router.post(
    '/{company_id}/departments',
    response_model=DepartmentRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def create_department(
    company_id: int, obj_in: DepartmentCreate, session: AsyncSession = Depends(get_async_session)
):
    await check_company_exists(company_id, session)
    try:
        department = await department_crud.create(obj_in, company_id, session)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=DEPARTMENT_NAME_EXISTS.format(company_id, obj_in.name)
        )
    return department


@router.patch(
    '/{company_id}/departments/{department_id}',
    response_model=DepartmentRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def update_department(
    company_id: int,
    department_id: int,
    obj_in: DepartmentUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        department = await department_crud.update(
            await check_department_in_company_exists(department_id, company_id, session), obj_in, session
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=DEPARTMENT_NAME_EXISTS.format(company_id, obj_in.name)
        )
    return department


@router.delete(
    '/{company_id}/departments/{department_id}',
    response_model=DepartmentRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def delete_department(company_id: int, department_id: int, session: AsyncSession = Depends(get_async_session)):
    department = await check_department_in_company_exists(department_id, company_id, session)
    return await department_crud.remove(department, session)


@router.post(
    '/{company_id}/invites',
    response_model=InviteRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def send_invite(
    obj_in: InviteCreate,
    company_id: int,
    background: BackgroundTasks,
    code: str = Depends(generate_invite_code),
    session: AsyncSession = Depends(get_async_session),
):
    await check_before_invite(obj_in, company_id, session)
    invite = await invites_crud.create(obj_in, company_id, code, session)
    background.add_task(send_invite_email, obj_in.email, code)
    return invite


@router.post('/invites/accept', response_model=CompanyMembershipRead, response_model_exclude_none=True)
async def accept_invite(
    code: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)
):
    invite = await check_invite_exists(code, session)
    try:
        membership = await membership_crud.create(
            CompanyMembershipCreate(
                user_id=user.id,
                company_id=invite.company_id,
                department_id=invite.department_id,
                manager_id=invite.manager_id,
                role=invite.role,
            ),
            session,
            user,
            commit=False,
        )
        await session.delete(invite)
        await session.commit()
        await session.refresh(membership)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=MEMBERSHIP_EXISTS.format(user.id, invite.company_id)
        )
    return membership
