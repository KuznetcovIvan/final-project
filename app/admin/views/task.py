from starlette_admin.contrib.sqla import ModelView

from app.models.task import Task, TaskComment


class TaskView(ModelView):
    def __init__(self):
        super().__init__(Task)
        self.name = 'Задачи'


class TaskCommentView(ModelView):
    def __init__(self):
        super().__init__(TaskComment)
        self.name = 'Комментарии'
