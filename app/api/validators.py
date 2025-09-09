from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.company import company_crud, department_crud, invites_crud, membership_crud, news_crud
from app.crud.task import task_comment_crud, task_crud
from app.models.company import Company, CompanyNews, Department, Invite, UserCompanyMembership, UserRole
from app.models.task import Task, TaskComment
from app.models.user import User
from app.schemas.company import CompanyMembershipUpdate, InviteCreate
from app.schemas.task import TaskUpdate

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
TASK_NOT_IN_COMPANY = 'Задача id={} не принадлежит компании id={}'
EXECUTOR_ONLY_STATUS = 'Исполнитель может изменять только статус'
CANNOT_MANAGE_TASK = 'У вас нет прав на редактирование (удаление) задачи id={}'
CANNOT_MANAGE_COMMENT = 'У вас нет прав на редактирование (удаление) комментария id={}'
COMMENT_NOT_FOUND = 'Комментарий id={} не найден в задаче id={}'


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


async def check_user_in_company(user_id: int, company_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await membership_crud.get_by_user_and_company(user_id, company_id, session)
    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=USER_MEMBERSHIP_NOT_FOUND.format(user_id, company_id)
        )
    return membership


async def check_before_leave(user_id: int, company_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await check_user_in_company(user_id, company_id, session)
    await check_last_admin(membership, company_id, session)
    return membership


async def check_executor_in_company(
    executor_user_id: int, company_id: int, session: AsyncSession
) -> UserCompanyMembership:
    await check_company_exists(company_id, session)
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


async def check_task_in_company(company_id, task_id, session):
    await check_company_exists(company_id, session)
    task = await task_crud.get_by_company(task_id, company_id, session)
    if task is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=TASK_NOT_IN_COMPANY.format(task_id, company_id))
    return task


async def check_has_full_task_access(user: User, company_id: int, task: Task, session: AsyncSession) -> bool:
    if user.is_superuser or user.id == task.author_id:
        return True
    membership = await membership_crud.get_by_user_and_company(user.id, company_id, session)
    return membership and membership.role == UserRole.ADMIN


async def check_has_full_comment_access(
    user: User, company_id: int, comment: TaskComment, session: AsyncSession
) -> bool:
    if user.is_superuser or user.id == comment.author_id:
        return True
    membership = await membership_crud.get_by_user_and_company(user.id, company_id, session)
    return membership and membership.role == UserRole.ADMIN


async def check_can_update_task(
    user: User, company_id: int, task: Task, obj_in: TaskUpdate, session: AsyncSession
) -> None:
    if await check_has_full_task_access(user, company_id, task, session):
        return
    if user.id == task.executor_id:
        obj_data = obj_in.model_dump(exclude_unset=True)
        if set(obj_data.keys()) - {'status'}:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=EXECUTOR_ONLY_STATUS)
        return
    raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=CANNOT_MANAGE_TASK.format(task.id))


async def check_can_delete_task(user: User, company_id: int, task: Task, session: AsyncSession) -> None:
    if not await check_has_full_task_access(user, company_id, task, session):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=CANNOT_MANAGE_TASK.format(task.id))


async def check_can_manage_comment(user: User, company_id: int, comment: TaskComment, session: AsyncSession) -> None:
    if not await check_has_full_comment_access(user, company_id, comment, session):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=CANNOT_MANAGE_COMMENT.format(comment.id))


async def check_comment_in_task_and_company(
    company_id: int, task_id: int, comment_id: int, session: AsyncSession
) -> TaskComment:
    await check_task_in_company(company_id, task_id, session)
    comment = await task_comment_crud.get_by_task(comment_id, task_id, session)
    if not comment:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=COMMENT_NOT_FOUND.format(comment_id, task_id))
    return comment
