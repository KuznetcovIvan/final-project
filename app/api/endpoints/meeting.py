from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import user_manager_admin_or_superuser, user_member_or_superuser
from app.api.validators import (
    check_can_manage_obj,
    check_user_in_company,
    check_user_is_not_busy,
    get_in_company_or_404,
)
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.meeting import attendee_crud, meeting_crud
from app.models.user import User
from app.schemas.meeting import MeetingAttendeeRead, MeetingCreate, MeetingRead, MeetingUpdate
from app.schemas.user import UserShortRead

router = APIRouter(tags=['Встречи'])


USER_IN_MEETINGS_EXISTS = 'Пользователь с id={} уже участвует в встрече id={}'


@router.post('/{company_id}/meetings', response_model=MeetingRead)
async def create_meeting(
    company_id: int,
    obj_in: MeetingCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(user_manager_admin_or_superuser),
):
    return await meeting_crud.create(obj_in, user, company_id, session)


@router.get(
    '/{company_id}/meetings', response_model=list[MeetingRead], dependencies=[Depends(user_member_or_superuser)]
)
async def get_all_meetings(company_id: int, session: AsyncSession = Depends(get_async_session)):
    return await meeting_crud.get_multi_by_company(company_id, session)


@router.patch('/{company_id}/meetings/{meeting_id}', response_model=MeetingRead)
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


@router.delete('/{company_id}/meetings/{meeting_id}', response_model=MeetingRead)
async def delete_meeting(
    company_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    meeting = await get_in_company_or_404(meeting_crud, meeting_id, company_id, session)
    await check_can_manage_obj(user, company_id, meeting, session)
    return await meeting_crud.remove(meeting, session)


@router.post('/{company_id}/meetings/{meeting_id}/invite/{invited_id}', response_model=MeetingAttendeeRead)
async def invite_meeting(
    company_id: int,
    meeting_id: int,
    invited_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    meeting = await get_in_company_or_404(meeting_crud, meeting_id, company_id, session)
    await check_can_manage_obj(user, company_id, meeting, session)
    await check_user_in_company(invited_id, company_id, session)
    await check_user_is_not_busy(invited_id, meeting.start_at, meeting.end_at, session)
    try:
        await attendee_crud.create(meeting_id, invited_id, session)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=USER_IN_MEETINGS_EXISTS.format(invited_id, meeting_id)
        )
    invited_users = await attendee_crud.get_users_from_meeting_attend(meeting_id, session)
    invited = [UserShortRead(id=user.id, email=user.email) for user in invited_users]
    return MeetingAttendeeRead(**jsonable_encoder(meeting), invited=invited)
