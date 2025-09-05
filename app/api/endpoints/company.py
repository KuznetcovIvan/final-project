from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_admin_or_superuser
from app.api.validators import check_company_exists, check_company_name_duplicate
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.company import company_crud, membership_crud
from app.models.company import UserRole
from app.models.user import User
from app.schemas.company import (
    CompanyCreate,
    CompanyMembershipCreate,
    CompanyMembershipRead,
    CompanyRead,
    CompanyUpdate,
)

router = APIRouter()


@router.post('/companies', response_model=CompanyMembershipRead, response_model_exclude_none=True)
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


@router.get('/companies', response_model=list[CompanyRead], response_model_exclude_none=True)
async def get_companies(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)):
    return await company_crud.get_multi_by_user(user, session)


@router.patch(
    '/companies/{company_id}',
    response_model=CompanyRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def update_company(company_id: int, obj_in: CompanyUpdate, session: AsyncSession = Depends(get_async_session)):
    return await company_crud.update(await check_company_exists(company_id, session), obj_in, session)


@router.delete(
    '/{company_id}',
    response_model=CompanyRead,
    response_model_exclude_none=True,
    dependencies=[Depends(user_admin_or_superuser)],
)
async def remove_company(company_id: int, session: AsyncSession = Depends(get_async_session)):
    return await company_crud.remove(await check_company_exists(company_id, session), session)
