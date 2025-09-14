from starlette_admin.exceptions import FormValidationError

from app.admin.views.base import BaseModelView
from app.models.task import Task, TaskComment
from app.schemas.task import TaskCommentCreate, TaskCreate


class TaskView(BaseModelView):
    def __init__(self):
        super().__init__(
            Task,
            TaskCreate,
            icon='fa fa-tasks',
            name='задачу',
            label='Задачи',
        )

    fields = ['id', 'title', 'body', 'status', 'company', 'author', 'executor', 'start_at', 'end_at']
    sortable_fields = ['id', 'status', 'start_at', 'end_at', 'title']
    searchable_fields = ['title', 'body']
    fields_default_sort = ['end_at']

    async def validate(self, request, data):
        if data.get('end_at') <= data.get('start_at'):
            raise FormValidationError({'end_at': 'Дата окончания должна быть позже даты начала!'})


class TaskCommentView(BaseModelView):
    def __init__(self):
        super().__init__(
            TaskComment,
            TaskCommentCreate,
            icon='fa fa-comments',
            name='комментарий',
            label='Комментарии к задачам',
        )

    fields = ['id', 'task', 'author', 'body']
    sortable_fields = ['id']
    searchable_fields = ['body']
    fields_default_sort = sortable_fields

    name = 'Комментарии'
