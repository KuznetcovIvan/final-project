from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import COMPANY_FIELD_NAME, DEPARTMENT_FIELD_NAME
from app.crud.company import company_crud, department_crud, news_crud
from app.models.company import Company, CompanyNews, Department
from app.schemas.company import CompanyUpdate, DepartmentCreate, DepartmentUpdate

PROJECT_NAME_EXISTS = 'Компания с именем "{}" уже существует!'
COMPANY_NOT_FOUND = 'Компания с id={} не найдена!'
NEWS_NOT_FOUND = 'В компании id={} нет новости с id={}!'
DEPARTMENT_NOT_FOUND = 'В компании id={} нет отдела с id={}!'
DEPARTMENT_EXISTS = 'В компании id={} уже существует отдел "{}"!'


async def check_company_exists(company_id: int, session: AsyncSession) -> Company:
    company = await company_crud.get(company_id, session)
    if company is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=COMPANY_NOT_FOUND.format(company_id))
    return company


async def check_company_name_duplicate(company_name: str, session: AsyncSession) -> None:
    if await company_crud.get_by_attribute(COMPANY_FIELD_NAME, company_name, session) is not None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=PROJECT_NAME_EXISTS.format(company_name))


async def check_company_before_edit(company_id: int, obj_in: CompanyUpdate, session: AsyncSession) -> Company:
    company = await check_company_exists(company_id, session)
    obj_data = obj_in.model_dump(exclude_unset=True)
    if COMPANY_FIELD_NAME in obj_data and obj_data[COMPANY_FIELD_NAME] != company.name:
        await check_company_name_duplicate(obj_data[COMPANY_FIELD_NAME], session)
    return company


async def check_news_in_company_exists(news_id: int, company_id: int, session: AsyncSession) -> CompanyNews:
    news = await news_crud.get(news_id, session)
    if news is None or news.company_id != company_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NEWS_NOT_FOUND.format(company_id, news_id))
    return news


async def check_department_name_duplicate_in_company(
    company_id: int, obj_in: DepartmentCreate, session: AsyncSession
) -> None:
    if await department_crud.exists_name_in_company(company_id, obj_in.name, session):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=DEPARTMENT_EXISTS.format(company_id, obj_in.name)
        )


async def check_department_in_company_exists(department_id: int, company_id: int, session: AsyncSession) -> Department:
    department = await department_crud.get(department_id, session)
    if department is None or department.company_id != company_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=DEPARTMENT_NOT_FOUND.format(company_id, department_id)
        )
    return department


async def check_department_before_edit(
    company_id: int, department_id: int, obj_in: DepartmentUpdate, session: AsyncSession
) -> Department:
    department = await check_department_in_company_exists(department_id, company_id, session)
    obj_data = obj_in.model_dump(exclude_unset=True)
    new_name = obj_data.get(DEPARTMENT_FIELD_NAME)
    if new_name is None or new_name == department.name:
        return department
    if await department_crud.exists_name_in_company(company_id, new_name, session):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=DEPARTMENT_EXISTS.format(company_id, new_name))
    return department
