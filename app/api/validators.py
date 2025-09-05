from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.company import company_crud
from app.models.company import Company

PROJECT_NAME_EXISTS = 'Компания с именем "{}" уже существует!'
COMPANY_NOT_FOUND = 'Компании с id={} не существует!'

# Написать валидатор (Присоединение через инвайт, Добавление сотрудника админом)
MEMBERSHIP_ALREADY_EXISTS = 'Пользователь уже в этой компании!'


async def check_company_name_duplicate(company_name: str, session: AsyncSession) -> None:
    if await company_crud.get_by_attribute('name', company_name, session) is not None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=PROJECT_NAME_EXISTS.format(company_name))


async def check_company_exists(company_id: int, session: AsyncSession) -> Company:
    company = await company_crud.get(company_id, session)
    if company is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=COMPANY_NOT_FOUND.format(company_id))
    return company
