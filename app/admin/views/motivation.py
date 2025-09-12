from app.admin.views.base import BaseModelView
from app.models.motivation import Rating


class RatingView(BaseModelView):
    def __init__(self):
        super().__init__(
            Rating,
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
