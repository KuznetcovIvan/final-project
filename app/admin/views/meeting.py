from starlette_admin.contrib.sqla import ModelView

from app.models.meeting import Meeting, MeetingAttendee


class MeetingView(ModelView):
    def __init__(self):
        super().__init__(Meeting)
        self.name = 'Встречи'


class MeetingAttendeeView(ModelView):
    def __init__(self):
        super().__init__(MeetingAttendee)
        self.name = 'Участники встреч'
