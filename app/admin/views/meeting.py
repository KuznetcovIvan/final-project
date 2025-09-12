from app.admin.views.base import BaseModelView
from app.models.meeting import Meeting, MeetingAttendee
from app.schemas.meeting import MeetingAttendeeAdminCreate, MeetingCreate


class MeetingView(BaseModelView):
    def __init__(self):
        super().__init__(
            Meeting,
            MeetingCreate,
            icon='fa fa-calendar',
            name='встречу',
            label='Встречи',
        )

    fields = ['id', 'title', 'description', 'company', 'author', 'start_at', 'end_at']
    sortable_fields = ['id', 'start_at', 'end_at', 'title']
    searchable_fields = ['title', 'description']
    fields_default_sort = ['start_at']


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
    sortable_fields = ['id', 'meeting', 'user']
    searchable_fields = ['id']
    fields_default_sort = searchable_fields
