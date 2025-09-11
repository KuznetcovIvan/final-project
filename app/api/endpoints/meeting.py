from enum import StrEnum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_manager_admin_or_superuser, user_member_or_superuser
from app.api.validators import check_can_manage_obj, get_in_company_or_404
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.meeting import meeting_crud
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingRead, MeetingUpdate

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


@router.get(
    '/{company_id}/meetings',
    response_model=list[MeetingRead],
    dependencies=[Depends(user_member_or_superuser)],
    tags=[MeetingTags.MEETINGS],
)
async def get_all_meetings(company_id: int, session: AsyncSession = Depends(get_async_session)):
    return await meeting_crud.get_multi_by_company(company_id, session)


@router.patch('/{company_id}/meetings/{meeting_id}', response_model=MeetingRead, tags=[MeetingTags.MEETINGS])
async def update_meeting(
    company_id: int,
    meeting_id: int,
    obj_in: MeetingUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    meeting = await get_in_company_or_404(meeting_crud, meeting_id, company_id, session)
    await check_can_manage_obj(user, company_id, meeting, session)
    return await meeting_crud.update(meeting, obj_in, session)


@router.delete('/{company_id}/meetings/{meeting_id}', response_model=MeetingRead, tags=[MeetingTags.MEETINGS])
async def delete_meeting(
    company_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    meeting = await get_in_company_or_404(meeting_crud, meeting_id, company_id, session)
    await check_can_manage_obj(user, company_id, meeting, session)
    return await meeting_crud.remove(meeting, session)
