from enum import StrEnum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_manager_admin_or_superuser, user_member_or_superuser
from app.api.validators import (
    check_can_delete_task,
    check_can_manage_comment,
    check_can_update_task,
    check_comment_in_task_and_company,
    check_manager_can_create_task,
    check_user_in_company,
    get_in_company_or_404,
)
from app.core.db import get_async_session
from app.crud.task import task_comment_crud, task_crud
from app.models.user import User
from app.schemas.task import TaskCommentCreate, TaskCommentRead, TaskCommentUpdate, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix='/companies')


class TaskTags(StrEnum):
    TASKS = 'Задачи'
    COMMENTS = 'Комментарии к задаче'


@router.post('/{company_id}/tasks', response_model=TaskRead, tags=[TaskTags.TASKS])
async def create_task(
    company_id: int,
    obj_in: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_manager_admin_or_superuser),
):
    executor_membership = await check_user_in_company(obj_in.executor_id, company_id, session)
    if not user.is_superuser:
        await check_manager_can_create_task(user.id, company_id, executor_membership, session)
    return await task_crud.create_for_company(obj_in, company_id, session, author=user)


@router.get(
    '/{company_id}/tasks',
    response_model=list[TaskRead],
    dependencies=[Depends(user_member_or_superuser)],
    tags=[TaskTags.TASKS],
)
async def get_all_tasks(company_id: int, session: AsyncSession = Depends(get_async_session)):
    return await task_crud.get_multi_by_company(company_id, session)


@router.patch('/{company_id}/tasks/{task_id}', response_model=TaskRead, tags=[TaskTags.TASKS])
async def update_task(
    company_id: int,
    task_id: int,
    obj_in: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_member_or_superuser),
):
    task = await get_in_company_or_404(task_crud, task_id, company_id, session)
    await check_can_update_task(user, company_id, task, obj_in, session)
    return await task_crud.update(task, obj_in, session)


@router.delete('/{company_id}/tasks/{task_id}', response_model=TaskRead, tags=[TaskTags.TASKS])
async def delete_task(
    company_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_member_or_superuser),
):
    task = await get_in_company_or_404(task_crud, task_id, company_id, session)
    await check_can_delete_task(user, company_id, task, session)
    return await task_crud.remove(task, session)


@router.post('/{company_id}/tasks/{task_id}/comments', response_model=TaskCommentRead, tags=[TaskTags.COMMENTS])
async def create_task_comment(
    company_id: int,
    task_id: int,
    obj_in: TaskCommentCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_member_or_superuser),
):
    await get_in_company_or_404(task_crud, task_id, company_id, session)
    return await task_comment_crud.create_for_task(obj_in, task_id, session, author=user)


@router.get(
    '/{company_id}/tasks/{task_id}/comments',
    response_model=list[TaskCommentRead],
    dependencies=[Depends(user_member_or_superuser)],
    tags=[TaskTags.COMMENTS],
)
async def get_all_task_comments(company_id: int, task_id: int, session: AsyncSession = Depends(get_async_session)):
    await get_in_company_or_404(task_crud, task_id, company_id, session)
    return await task_comment_crud.get_multi_by_task(task_id, session)


@router.patch(
    '/{company_id}/tasks/{task_id}/comments/{comment_id}', response_model=TaskCommentRead, tags=[TaskTags.COMMENTS]
)
async def update_task_comment(
    company_id: int,
    task_id: int,
    comment_id: int,
    obj_in: TaskCommentUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_member_or_superuser),
):
    comment = await check_comment_in_task_and_company(company_id, task_id, comment_id, session)
    await check_can_manage_comment(user, company_id, comment, session)
    return await task_comment_crud.update(comment, obj_in, session)


@router.delete(
    '/{company_id}/tasks/{task_id}/comments/{comment_id}', response_model=TaskCommentRead, tags=[TaskTags.COMMENTS]
)
async def delete_task_comment(
    company_id: int,
    task_id: int,
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_member_or_superuser),
):
    comment = await check_comment_in_task_and_company(company_id, task_id, comment_id, session)
    await check_can_manage_comment(user, company_id, comment, session)
    return await task_comment_crud.remove(comment, session)
