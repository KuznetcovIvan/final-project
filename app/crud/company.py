from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.company import Company, Department, UserCompanyMembership
from app.models.user import User


class CRUDCompany(CRUDBase):
    async def get_multi_by_user(self, user: User, session: AsyncSession):
        if user.is_superuser:
            query = select(self.model).options(selectinload(self.model.memberships))
        else:
            query = (
                select(Company)
                .join(UserCompanyMembership)
                .where(UserCompanyMembership.user_id == user.id)
                .options(selectinload(Company.memberships))
            )
        result = await session.execute(query)
        return result.scalars().all()


class CRUDDepartment(CRUDBase):
    pass


class CRUDMembership(CRUDBase):
    pass


company_crud = CRUDCompany(Company)
department_crud = CRUDDepartment(Department)
membership_crud = CRUDMembership(UserCompanyMembership)
