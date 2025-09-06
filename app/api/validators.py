from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.company import company_crud, department_crud, news_crud
from app.models.company import Company, CompanyNews, Department

COMPANY_NOT_FOUND = 'Компания с id={} не найдена!'
NEWS_NOT_FOUND = 'В компании id={} нет новости с id={}!'
DEPARTMENT_NOT_FOUND = 'В компании id={} нет отдела с id={}!'


async def check_company_exists(company_id: int, session: AsyncSession) -> Company:
    company = await company_crud.get(company_id, session)
    if company is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=COMPANY_NOT_FOUND.format(company_id))
    return company


async def check_news_in_company_exists(news_id: int, company_id: int, session: AsyncSession) -> CompanyNews:
    news = await news_crud.get(news_id, session)
    if news is None or news.company_id != company_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NEWS_NOT_FOUND.format(company_id, news_id))
    return news


async def check_department_in_company_exists(department_id: int, company_id: int, session: AsyncSession) -> Department:
    department = await department_crud.get(department_id, session)
    if department is None or department.company_id != company_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=DEPARTMENT_NOT_FOUND.format(company_id, department_id)
        )
    return department
