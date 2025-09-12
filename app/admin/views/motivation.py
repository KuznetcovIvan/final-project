from starlette_admin.exceptions import FormValidationError

from app.admin.views.base import BaseModelView
from app.core.db import AsyncSessionLocal
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
        fields = dict(
            timeliness=data.get('timeliness'), completeness=data.get('completeness'), quality=data.get('quality')
        )
        for field, value in fields.items():
            if not 1 <= int(value) <= 5:
                errors[field] = f'Значение {field} должно быть от 1 до 5'
        if not data.get('created_at'):
            errors['created_at'] = 'Выберите дату'
        task = data.get('task')
        if task:
            async with AsyncSessionLocal() as session:
                db_task = await session.get(Task, task.id)
                if not db_task or db_task.status != TaskStatus.DONE:
                    errors['task'] = 'Оценку можно выставить только завершённой задаче'
        else:
            errors['task'] = 'Не выбрана задача для оценки'
        if errors:
            raise FormValidationError(errors)
