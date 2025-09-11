from enum import StrEnum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_manager_admin_or_superuser
from app.core.db import get_async_session
from app.crud.meeting import meeting_crud
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingRead

router = APIRouter()


class MeetingTags(StrEnum):
    MEETINGS = 'Встречи'


@router.post('/{company_id}/meetings', response_model=MeetingRead, tags=[MeetingTags.MEETINGS])
async def create_meeting(
    company_id: int,
    obj_in: MeetingCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_manager_admin_or_superuser),
):
    return await meeting_crud.create(obj_in, user, company_id, session)


router
