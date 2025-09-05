from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.crud.company import company_crud, news_crud
from app.models.company import Company, CompanyNews

PROJECT_NAME_EXISTS = 'Компания с именем "{}" уже существует!'
NEWS_NOT_FOUND = 'В компании id={} нет новости с id={}!'
COMPANY_NOT_FOUND = 'Компания с id={} не найдена!'
OBJ_NOT_FOUND = 'Объект с id={} не найден!'

# Написать валидатор (Присоединение через инвайт, Добавление сотрудника админом)
MEMBERSHIP_ALREADY_EXISTS = 'Пользователь уже в этой компании!'


async def check_company_name_duplicate(company_name: str, session: AsyncSession) -> None:
    if await company_crud.get_by_attribute('name', company_name, session) is not None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=PROJECT_NAME_EXISTS.format(company_name))


async def check_company_exists(company_id: int, session: AsyncSession) -> Company:
    company = await company_crud.get(company_id, session)
    if company is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=COMPANY_NOT_FOUND.format(company_id),
        )
    return company


async def check_news_in_company_exists(news_id: int, company_id: int, session: AsyncSession) -> CompanyNews:
    news = await news_crud.get(news_id, session)
    if news is None or news.company_id != company_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NEWS_NOT_FOUND.format(company_id, news_id))
    return news


async def check_obj_exists(obj_id: int, crud: CRUDBase, session: AsyncSession):
    obj = await crud.get(obj_id, session)
    if obj is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=OBJ_NOT_FOUND.format(obj_id))
    return obj
