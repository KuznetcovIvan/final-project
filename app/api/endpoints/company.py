from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_admin_or_superuser, user_member_or_superuser
from app.api.validators import (
    check_company_before_edit,
    check_company_exists,
    check_company_name_duplicate,
    check_department_before_edit,
    check_department_in_company_exists,
    check_department_name_duplicate_in_company,
    check_news_in_company_exists,
)
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.company import company_crud, department_crud, membership_crud, news_crud
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
)

router = APIRouter(prefix='/companies')


@router.post('/', response_model=CompanyMembershipRead, response_model_exclude_none=True)
async def create_new_company(
    company: CompanyCreate, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)
):
    await check_company_name_duplicate(company.name, session)
    new_company = await company_crud.create(company, session, commit=False)
    await session.flush()
    new_membership = await membership_crud.create(
        CompanyMembershipCreate(user_id=user.id, company_id=new_company.id, role=UserRole.ADMIN),
        session=session,
        commit=False,
    )
    await session.commit()
    await session.refresh(new_membership)
    return new_membership


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
    return await company_crud.update(await check_company_before_edit(company_id, obj_in, session), obj_in, session)


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
async def get_all_news(
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
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
    await check_department_name_duplicate_in_company(company_id, obj_in, session)
    return await department_crud.create(obj_in, company_id, session)


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
    department = await check_department_before_edit(company_id, department_id, obj_in, session)
    return await department_crud.update(department, obj_in, session)


@router.delete(
    '/{company_id}/departments/{department_id}',
    response_model=DepartmentRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def delete_department(company_id: int, department_id: int, session: AsyncSession = Depends(get_async_session)):
    department = await check_department_in_company_exists(department_id, company_id, session)
    return await department_crud.remove(department, session)
