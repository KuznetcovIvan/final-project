from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user
from app.models.company import UserCompanyMembership as Membership
from app.models.company import UserRole
from app.models.user import User

NOT_COMPANY_ADMIN = 'Вы должны быть админом этой компании или суперпользователем'


async def user_admin_or_superuser(
    company_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)
) -> User:
    if user.is_superuser:
        return user
    result = await session.execute(
        select(
            exists().where(
                Membership.user_id == user.id, Membership.company_id == company_id, Membership.role == UserRole.ADMIN
            )
        )
    )
    if not result.scalar():
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=NOT_COMPANY_ADMIN)
    return user
