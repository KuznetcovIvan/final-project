from sqlalchemy import select
from starlette_admin.exceptions import FormValidationError

from app.admin.views.base import BaseModelView
from app.models.motivation import Rating
from app.models.task import Task, TaskStatus
from app.schemas.motivation import RatingCreate


class RatingView(BaseModelView):
    def __init__(self):
        super().__init__(
            Rating,
            RatingCreate,
            icon='fa fa-star',
            name='оценку',
            label='Оценки',
        )

    fields = ['id', 'task', 'timeliness', 'completeness', 'quality', 'avg', 'created_at']
    exclude_fields_from_create = ['avg']
    exclude_fields_from_edit = exclude_fields_from_create
    sortable_fields = ['id', 'avg', 'created_at']
    searchable_fields = ['id']
    fields_default_sort = ['created_at']

    async def validate(self, request, data):
        errors = {}
        task = data.get('task')
        if not task:
            errors['task'] = 'Не выбрана задача для оценки'
        else:
            session = request.state.session
            db_task = await session.get(Task, task.id)
            if not db_task or db_task.status != TaskStatus.DONE:
                errors['task'] = 'Оценку можно выставить только завершённой задаче'
            if await session.scalar(select(Rating.id).where(Rating.task_id == task.id)):
                errors['task'] = 'Эта задача уже была оценена'
        if errors:
            raise FormValidationError(errors)
        return data
