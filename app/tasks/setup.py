from apscheduler.triggers.cron import CronTrigger

from app.core.constants import TIME_CLEANUP_INVITES
from app.core.scheduler import scheduler
from app.tasks.invites import cleanup_expired_invites_task


def register_jobs():
    scheduler.add_job(
        cleanup_expired_invites_task, CronTrigger(**TIME_CLEANUP_INVITES), id='cleanup_invites', replace_existing=True
    )
