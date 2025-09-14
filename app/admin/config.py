from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin
from starlette_admin.i18n import I18nConfig

from app.admin.auth import ADMIN_TITLE, SuperuserAuth
from app.admin.views.company import CompanyView, DepartmentView, InviteView, MembershipView, NewsView
from app.admin.views.meeting import MeetingAttendeeView, MeetingView
from app.admin.views.motivation import RatingView
from app.admin.views.task import TaskCommentView, TaskView
from app.admin.views.user import UserView
from app.core.config import settings
from app.core.db import engine

views = (
    UserView,
    CompanyView,
    DepartmentView,
    MembershipView,
    InviteView,
    NewsView,
    MeetingView,
    MeetingAttendeeView,
    TaskView,
    TaskCommentView,
    RatingView,
)


def init_admin(app: FastAPI) -> Admin:
    admin = Admin(
        engine,
        title=ADMIN_TITLE,
        auth_provider=SuperuserAuth(),
        middlewares=[Middleware(SessionMiddleware, secret_key=settings.secret)],
        i18n_config=I18nConfig(default_locale='ru'),
    )
    for view in views:
        admin.add_view(view())

    admin.mount_to(app)
    return admin
