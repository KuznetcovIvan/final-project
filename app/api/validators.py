from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.company import company_crud, department_crud, invites_crud, membership_crud, news_crud
from app.models.company import Company, CompanyNews, Department, Invite, UserRole
from app.schemas.company import InviteCreate

COMPANY_NOT_FOUND = 'Компания с id={} не найдена!'
NEWS_NOT_FOUND = 'В компании id={} нет новости с id={}!'
DEPARTMENT_NOT_FOUND = 'В компании id={} нет отдела с id={}!'
INVITE_NOT_FOUND = 'Код приглашения "{}" не найден или устарел!'
MANAGER_NOT_IN_COMPANY = 'Пользователь id={} не состоит в компании id={}.'
MANAGER_ROLE_REQUIRED = 'Пользователь id={} не менеджер и не админ компании id={}.'


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


async def check_invite_exists(code: str, session: AsyncSession) -> Invite:
    invite = await invites_crud.get_by_attribute('code', code, session)
    if not invite:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=INVITE_NOT_FOUND.format(code))
    return invite


async def check_manager_in_company(manager_id: int, company_id: int, session):
    membership = await membership_crud.get_by_user_and_company(manager_id, company_id, session)
    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=MANAGER_NOT_IN_COMPANY.format(manager_id, company_id),
        )
    if membership.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=MANAGER_ROLE_REQUIRED.format(manager_id, company_id),
        )


async def check_before_invite(obj_in: InviteCreate, company_id: int, session: AsyncSession):
    if obj_in.department_id is None:
        await check_company_exists(company_id, session)
    else:
        await check_department_in_company_exists(obj_in.department_id, company_id, session)
    if obj_in.manager_id is not None:
        await check_manager_in_company(obj_in.manager_id, company_id, session)
