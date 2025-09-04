from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_company_name_duplicate
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.company import company_crud, membership_crud
from app.models.company import UserRole
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyMembershipCreate, CompanyMembershipRead

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
