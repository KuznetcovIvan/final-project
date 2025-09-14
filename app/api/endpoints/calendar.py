from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_user_in_company
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.calendar import CalendarService
from app.models.user import User
from app.schemas.calendar import CalendarRead, CalendarScope

router = APIRouter(tags=['Календарь'])


@router.get('/{company_id}/calendar/{scope}', response_model=CalendarRead)
async def get_events(
    company_id: int,
    scope: CalendarScope,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    await check_user_in_company(user.id, company_id, session)
    events = CalendarService(company_id, user.id, scope, session)
    return CalendarRead(
        scope=scope,
        news=await events.fetch_news(),
        tasks=await events.fetch_tasks(),
        meetings=await events.fetch_meetings(),
    )
