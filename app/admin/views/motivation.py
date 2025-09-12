from starlette_admin.contrib.sqla import ModelView

from app.models.motivation import Rating


class RatingView(ModelView):
    def __init__(self):
        super().__init__(Rating)
        self.name = 'Оценки'
