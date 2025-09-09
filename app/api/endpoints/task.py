from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_manager_admin_or_superuser
from app.api.validators import check_company_exists, check_executor_in_company, check_manager_can_create_task
from app.core.db import get_async_session
from app.crud.task import task_crud
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(prefix='/companies', tags=['Задачи'])


@router.post('/{company_id}/tasks', response_model=TaskRead)
async def create_task(
    company_id: int,
    obj_in: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_manager_admin_or_superuser),
):
    await check_company_exists(company_id, session)
    executor_membership = await check_executor_in_company(obj_in.executor_id, company_id, session)
    if not user.is_superuser:
        await check_manager_can_create_task(user.id, company_id, executor_membership, session)
    return await task_crud.create_for_company(obj_in, company_id, session, author=user)
