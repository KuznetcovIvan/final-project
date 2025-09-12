from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.constants import TIME_CLEANUP_INVITES
from app.tasks.invites import cleanup_expired_invites_task

scheduler = AsyncIOScheduler(job_defaults={'coalesce': True, 'max_instances': 1, 'misfire_grace_time': 10 * 60})


def start_scheduler():
    if not scheduler.running:
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()


def register_jobs():
    scheduler.add_job(
        cleanup_expired_invites_task, CronTrigger(**TIME_CLEANUP_INVITES), id='cleanup_invites', replace_existing=True
    )
