from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.company import membership_crud
from app.models.company import UserRole
from app.models.user import User

NOT_COMPANY_ADMIN = 'Требуются права администратора компании или суперпользователя!'
NOT_COMPANY_MEMBER = 'Вы не являетесь работником этой компании!'
NOT_MANAGER_OR_ADMIN = 'Требуются права менеджера, администратора или суперпользователя!'


async def user_admin_or_superuser(
    company_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)
) -> User:
    if user.is_superuser:
        return user
    membership = await membership_crud.get_by_user_and_company(user.id, company_id, session)
    if membership is None or membership.role != UserRole.ADMIN:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=NOT_COMPANY_ADMIN)
    return user


async def user_member_or_superuser(
    company_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if user.is_superuser:
        return user
    membership = await membership_crud.get_by_user_and_company(user.id, company_id, session)
    if membership is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=NOT_COMPANY_MEMBER)
    return user


async def user_manager_admin_or_superuser(
    company_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)
) -> User:
    if user.is_superuser:
        return user
    membership = await membership_crud.get_by_user_and_company(user.id, company_id, session)
    if membership is None or membership.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=NOT_MANAGER_OR_ADMIN)
    return user
