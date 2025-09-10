from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.crud.company import company_crud, department_crud, invites_crud, membership_crud
from app.crud.task import task_comment_crud, task_crud
from app.models.company import Invite, UserCompanyMembership, UserRole
from app.models.task import Task, TaskComment
from app.models.user import User
from app.schemas.company import CompanyMembershipUpdate, InviteCreate
from app.schemas.task import TaskUpdate

NOT_FOUND = '{} c id={} не найден!'
NOT_FOUND_IN_COMPANY = '{} id={} не найден(а) в компании id={}!'
NOT_FOUND_USER_IN_COMPANY = 'Пользователь id={} не состоит в компании id={}!'
INVITE_NOT_FOUND = 'Инвайт {} не найден или устарел!'
INVITE_EMAIL_MISMATCH = 'Инвайт не предназначен для {}!'
MANAGER_ROLE_REQUIRED = 'Пользователь id={} не менеджер и не админ!'
LAST_ADMIN_FORBIDDEN = 'Нельзя удалить единственного администратора!'
SELF_MANAGER_FORBIDDEN = 'Нельзя назначить менеджером самого себя!'
ONLY_SUBORDINATES = 'Можно назначать задачи только подчинённым!'
EXECUTOR_ONLY_STATUS = 'Исполнитель может менять только статус!'
CANNOT_EDIT_TASK = 'У пользователя id={} нет прав на редактирование задачи {}!'
CANNOT_DELETE_TASK = 'У пользователя id={} нет прав на удаление задачи {}!'
CANNOT_EDIT_COMMENT = 'У пользователя id={} нет прав на редактирование комментария {}!'
COMMENT_NOT_FOUND = 'Комментарий id={} не найден в задаче id={}!'


async def get_or_404(crud: CRUDBase, obj_id: int, session: AsyncSession):
    obj = await crud.get(obj_id, session)
    if obj is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND.format(crud.model.__name__, obj_id))
    return obj


async def get_in_company_or_404(crud: CRUDBase, obj_id: int, company_id: int, session: AsyncSession):
    obj = await crud.get(obj_id, session)
    if obj is None or obj.company_id != company_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=NOT_FOUND_IN_COMPANY.format(crud.model.__name__, obj_id, company_id),
        )
    return obj


async def check_user_in_company(user_id: int, company_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await membership_crud.get_by_user_and_company(user_id, company_id, session)
    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_USER_IN_COMPANY.format(user_id, company_id)
        )
    return membership


async def check_invite_exists(code: str, user: User, session: AsyncSession) -> Invite:
    invite = await invites_crud.get_by_attribute('code', code, session)
    if not invite or invite.expires_at < datetime.now():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=INVITE_NOT_FOUND.format(code))
    if invite.email.strip().lower() != user.email.strip().lower():
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=INVITE_EMAIL_MISMATCH.format(user.email))
    return invite


async def check_manager_in_company(manager_id: int, company_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await check_user_in_company(manager_id, company_id, session)
    if membership.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=MANAGER_ROLE_REQUIRED.format(manager_id))
    return membership


async def check_last_admin(membership: UserCompanyMembership, company_id: int, session: AsyncSession):
    if membership.role == UserRole.ADMIN and await membership_crud.count_company_admins(company_id, session) <= 1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=LAST_ADMIN_FORBIDDEN)


async def check_before_invite(obj_in: InviteCreate, company_id: int, session: AsyncSession):
    if obj_in.department_id:
        await get_in_company_or_404(department_crud, obj_in.department_id, company_id, session)
    else:
        await get_or_404(company_crud, company_id, session)
    if obj_in.manager_id:
        await check_manager_in_company(obj_in.manager_id, company_id, session)


async def check_before_update_membership(
    obj_in: CompanyMembershipUpdate, company_id: int, membership: UserCompanyMembership, session: AsyncSession
):
    if obj_in.department_id:
        await get_in_company_or_404(department_crud, obj_in.department_id, company_id, session)
    if obj_in.manager_id is not None:
        if obj_in.manager_id == membership.user_id:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=SELF_MANAGER_FORBIDDEN)
        await check_manager_in_company(obj_in.manager_id, company_id, session)
    if obj_in.role and obj_in.role != UserRole.ADMIN and membership.role == UserRole.ADMIN:
        await check_last_admin(membership, company_id, session)


async def check_before_delete_membership(
    membership_id: int, company_id: int, session: AsyncSession
) -> UserCompanyMembership:
    membership = await get_in_company_or_404(membership_crud, membership_id, company_id, session)
    await check_last_admin(membership, company_id, session)
    return membership


async def check_before_leave(user_id: int, company_id: int, session: AsyncSession) -> UserCompanyMembership:
    membership = await check_user_in_company(user_id, company_id, session)
    await check_last_admin(membership, company_id, session)
    return membership


async def has_full_access(user: User, company_id: int, obj: Task | TaskComment, session: AsyncSession) -> bool:
    if user.is_superuser or user.id == obj.author_id:
        return True
    membership = await membership_crud.get_by_user_and_company(user.id, company_id, session)
    return bool(membership and membership.role == UserRole.ADMIN)


async def check_manager_can_create_task(
    manager_id: int, company_id: int, executor_membership: UserCompanyMembership, session: AsyncSession
):
    manager_membership = await check_manager_in_company(manager_id, company_id, session)
    if manager_membership.role == UserRole.ADMIN:
        return
    if manager_membership.role == UserRole.MANAGER and executor_membership.manager_id != manager_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=ONLY_SUBORDINATES)


async def check_can_update_task(user: User, company_id: int, task: Task, obj_in: TaskUpdate, session: AsyncSession):
    if await has_full_access(user, company_id, task, session):
        return
    if user.id == task.executor_id:
        obj_data = obj_in.model_dump(exclude_unset=True)
        if set(obj_data.keys()) - {'status'}:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=EXECUTOR_ONLY_STATUS)
        return
    raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=CANNOT_EDIT_TASK.format(user.id, task.id))


async def check_can_delete_task(user: User, company_id: int, task: Task, session: AsyncSession):
    if not await has_full_access(user, company_id, task, session):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=CANNOT_DELETE_TASK.format(user.id, task.id))


async def check_can_manage_comment(user: User, company_id: int, comment: TaskComment, session: AsyncSession):
    if not await has_full_access(user, company_id, comment, session):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=CANNOT_EDIT_COMMENT.format(user.id, comment.id))


async def check_comment_in_task_and_company(
    company_id: int, task_id: int, comment_id: int, session: AsyncSession
) -> TaskComment:
    await get_in_company_or_404(task_crud, task_id, company_id, session)
    comment = await task_comment_crud.get_by_task(comment_id, task_id, session)
    if not comment:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=COMMENT_NOT_FOUND.format(comment_id, task_id))
    return comment
