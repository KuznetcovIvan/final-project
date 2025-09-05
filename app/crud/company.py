from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.company import Company, CompanyNews, Department, UserCompanyMembership
from app.models.user import User
from app.schemas.company import CompanyNewsCreate, DepartmentCreate


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
    async def create(self, obj_in: DepartmentCreate, company_id: int, session: AsyncSession):
        data = obj_in.model_dump()
        data['company_id'] = company_id
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


async def get_multi_by_company(self, company_id: int, session: AsyncSession):
    result = await session.execute(select(self.model).where(self.model.company_id == company_id))
    return result.scalars().all()


class CRUDMembership(CRUDBase):
    pass


class CRUDNews(CRUDBase):
    async def create(self, obj_in: CompanyNewsCreate, user: User, company_id: int, session: AsyncSession):
        data = obj_in.model_dump()
        data['author_id'] = user.id
        data['company_id'] = company_id
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_company(self, company_id: int, session: AsyncSession):
        result = await session.execute(select(self.model).where(self.model.company_id == company_id))
        return result.scalars().all()


company_crud = CRUDCompany(Company)
department_crud = CRUDDepartment(Department)
membership_crud = CRUDMembership(UserCompanyMembership)
news_crud = CRUDNews(CompanyNews)
