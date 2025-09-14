from datetime import datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import INVITE_CODE_DAYS_TTL
from app.crud.base import CRUDBase
from app.models.company import Company, CompanyNews, Department, Invite, UserCompanyMembership, UserRole
from app.models.user import User
from app.schemas.company import CompanyNewsCreate, DepartmentCreate, InviteCreate


class CRUDCompanyBase(CRUDBase):
    async def get_multi_by_company(self, company_id: int, session: AsyncSession):
        result = await session.execute(select(self.model).where(self.model.company_id == company_id))
        return result.scalars().all()

    async def _create_and_return(self, data: dict, session: AsyncSession):
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


class CRUDCompany(CRUDCompanyBase):
    async def get_multi_by_user(self, user: User, session: AsyncSession):
        query = select(self.model).options(selectinload(self.model.memberships))
        if not user.is_superuser:
            query = query.join(UserCompanyMembership).where(UserCompanyMembership.user_id == user.id)
        result = await session.execute(query)
        return result.scalars().all()


class CRUDDepartment(CRUDCompanyBase):
    async def create(self, obj_in: DepartmentCreate, company_id: int, session: AsyncSession):
        data = obj_in.model_dump()
        data['company_id'] = company_id
        return await self._create_and_return(data, session)


class CRUDMembership(CRUDCompanyBase):
    async def get_by_user_and_company(self, user_id: int, company_id: int, session: AsyncSession):
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id, self.model.company_id == company_id)
        )
        return result.scalars().first()

    async def count_company_admins(self, company_id: int, session: AsyncSession):
        result = await session.execute(
            select(func.count()).where(self.model.company_id == company_id, self.model.role == UserRole.ADMIN)
        )
        return result.scalar_one()


class CRUDNews(CRUDCompanyBase):
    async def create(self, obj_in: CompanyNewsCreate, user: User, company_id: int, session: AsyncSession):
        data = obj_in.model_dump()
        data['author_id'] = user.id
        data['company_id'] = company_id
        return await self._create_and_return(data, session)


class CRUDInvites(CRUDCompanyBase):
    async def create(self, obj_in: InviteCreate, company_id: int, code: str, session: AsyncSession):
        data = obj_in.model_dump()
        data['code'] = code
        data['company_id'] = company_id
        data['expires_at'] = datetime.now() + timedelta(days=INVITE_CODE_DAYS_TTL)
        return await self._create_and_return(data, session)

    async def cleanup_expired_invites(self, session: AsyncSession):
        await session.execute(delete(self.model).where(self.model.expires_at < datetime.now()))
        await session.commit()


company_crud = CRUDCompany(Company)
department_crud = CRUDDepartment(Department)
membership_crud = CRUDMembership(UserCompanyMembership)
news_crud = CRUDNews(CompanyNews)
invites_crud = CRUDInvites(Invite)
