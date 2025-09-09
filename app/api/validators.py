from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.company import company_crud, department_crud, invites_crud, membership_crud, news_crud
from app.models.company import Company, CompanyNews, Department, Invite, UserCompanyMembership, UserRole
from app.models.user import User
from app.schemas.company import CompanyMembershipUpdate, InviteCreate

COMPANY_NOT_FOUND = 'Компания с id={} не найдена!'
MEMBERSHIP_NOT_FOUND = 'Участник с membership_id={} не найден!'
USER_MEMBERSHIP_NOT_FOUND = 'Пользователь id={} не состоит в компании id={}.'
NEWS_NOT_FOUND = 'В компании id={} нет новости с id={}!'
DEPARTMENT_NOT_FOUND = 'В компании id={} нет отдела с id={}!'
INVITE_NOT_FOUND = 'Код приглашения "{}" не найден или устарел!'
INVITE_EMAIL_MISMATCH = 'Инвайт предназначен для другого адреса почты!'
MANAGER_NOT_IN_COMPANY = 'Пользователь id={} не состоит в компании id={}.'
MANAGER_ROLE_REQUIRED = 'Пользователь id={} не менеджер и не админ компании id={}.'
SELF_MANAGER_FORBIDDEN = 'Нельзя назначить менеджером самого себя.'
LAST_ADMIN_FORBIDDEN = 'Нельзя удалить единственного администратора компании.'
EXECUTOR_NOT_IN_COMPANY = 'Исполнитель с id={} не состоит в этой компании!'
ONLY_SUBORDINATES = 'Исполнитель с id={} не подчиняется пользователю с id={}!'


async def check_company_exists(company_id: int, session: AsyncSession) -> Company:
    company = await company_crud.get(company_id, session)
    if company is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=COMPANY_NOT_FOUND.format(company_id))
    return company


async def check_membership_exists(membership_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await membership_crud.get(membership_id, session)
    if membership is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=MEMBERSHIP_NOT_FOUND.format(membership_id))
    return membership


async def check_membership_in_company_exists(
    membership_id: int, company_id: int, session: AsyncSession
) -> UserCompanyMembership:
    membership = await check_membership_exists(membership_id, session)
    if membership.company_id != company_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=MEMBERSHIP_NOT_FOUND.format(membership_id))
    return membership


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


async def check_invite_exists(code: str, user: User, session: AsyncSession) -> Invite:
    invite = await invites_crud.get_by_attribute('code', code, session)
    if not invite or invite.expires_at < datetime.now():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=INVITE_NOT_FOUND.format(code))
    if invite.email.strip().lower() != user.email.strip().lower():
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=INVITE_EMAIL_MISMATCH)
    return invite


async def check_manager_in_company(manager_id: int, company_id: int, session) -> UserCompanyMembership:
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
    return membership


async def check_before_invite(obj_in: InviteCreate, company_id: int, session: AsyncSession):
    if obj_in.department_id is None:
        await check_company_exists(company_id, session)
    else:
        await check_department_in_company_exists(obj_in.department_id, company_id, session)
    if obj_in.manager_id is not None:
        await check_manager_in_company(obj_in.manager_id, company_id, session)


async def check_last_admin(membership: UserCompanyMembership, company_id: int, session: AsyncSession):
    if membership.role == UserRole.ADMIN and await membership_crud.count_company_admins(company_id, session) <= 1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=LAST_ADMIN_FORBIDDEN)


async def check_before_update_membership(
    obj_in: CompanyMembershipUpdate, company_id: int, membership: UserCompanyMembership, session: AsyncSession
):
    if obj_in.department_id is not None:
        await check_department_in_company_exists(obj_in.department_id, company_id, session)
    if obj_in.manager_id is not None:
        if obj_in.manager_id == membership.user_id:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=SELF_MANAGER_FORBIDDEN)
        await check_manager_in_company(obj_in.manager_id, company_id, session)
    if obj_in.role is not None and obj_in.role != UserRole.ADMIN and membership.role == UserRole.ADMIN:
        await check_last_admin(membership, company_id, session)


async def check_before_delete_membership(
    membership_id: int, company_id: int, session: AsyncSession
) -> UserCompanyMembership:
    membership = await check_membership_in_company_exists(membership_id, company_id, session)
    await check_last_admin(membership, company_id, session)
    return membership


async def check_before_leave(user_id: int, company_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await membership_crud.get_by_user_and_company(user_id, company_id, session)
    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=USER_MEMBERSHIP_NOT_FOUND.format(user_id, company_id)
        )
    await check_last_admin(membership, company_id, session)
    return membership


async def check_executor_in_company(
    executor_user_id: int, company_id: int, session: AsyncSession
) -> UserCompanyMembership:
    membership = await membership_crud.get_by_user_and_company(executor_user_id, company_id, session)
    if membership is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=EXECUTOR_NOT_IN_COMPANY.format(executor_user_id))
    return membership


async def check_manager_can_create_task(
    manager_id: int, company_id: int, executor_membership, session: AsyncSession
) -> None:
    manager_membership = await check_manager_in_company(manager_id, company_id, session)
    if manager_membership.role == UserRole.ADMIN:
        return
    if manager_membership.role == UserRole.MANAGER and executor_membership.manager_id != manager_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=ONLY_SUBORDINATES.format(executor_membership.user_id, manager_id)
        )
