from sqlalchemy import select
from starlette_admin.exceptions import FormValidationError

from app.admin.views.base import BaseModelView
from app.models.meeting import Meeting, MeetingAttendee
from app.schemas.meeting import MeetingAdminCreate, MeetingAttendeeAdminCreate


class MeetingView(BaseModelView):
    def __init__(self):
        super().__init__(
            Meeting,
            MeetingAdminCreate,
            icon='fa fa-calendar',
            name='встречу',
            label='Встречи',
        )

    fields = ['id', 'title', 'description', 'company', 'author', 'start_at', 'end_at']
    sortable_fields = ['id', 'start_at', 'end_at', 'title']
    searchable_fields = ['title', 'description']
    fields_default_sort = ['start_at']

    async def validate(self, request, data):
        errors = {}
        for field in ('author', 'company'):
            if not data.get(field):
                errors[field] = f'Поле {field} обязательно!'
        if data.get('end_at') <= data.get('start_at'):
            errors['end_at'] = 'Дата окончания должна быть позже даты начала!'
        if errors:
            raise FormValidationError(errors)
        return data


class MeetingAttendeeView(BaseModelView):
    def __init__(self):
        super().__init__(
            MeetingAttendee,
            MeetingAttendeeAdminCreate,
            icon='fa fa-user-check',
            name='участника встречи',
            label='Участники встреч',
        )

    fields = ['id', 'meeting', 'user']
    sortable_fields = ['id']
    searchable_fields = ['id']
    fields_default_sort = searchable_fields

    async def validate(self, request, data):
        errors = {}
        meeting = data.get('meeting')
        user = data.get('user')
        if not meeting:
            errors['meeting'] = 'Выберите встречу'
        if not user:
            errors['user'] = 'Выберите пользователя'
        if not errors:
            session = request.state.session
            attendee_id = request.path_params.get('pk')
            query = select(MeetingAttendee.id).where(
                MeetingAttendee.meeting_id == meeting.id,
                MeetingAttendee.user_id == user.id,
            )
            if attendee_id:
                query = query.where(MeetingAttendee.id != int(attendee_id))
            if await session.scalar(query):
                errors['user'] = 'Пользователь уже добавлен в участники этой встречи'
        if errors:
            raise FormValidationError(errors)
        return data
