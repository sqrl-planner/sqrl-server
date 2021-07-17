"""Celery tasks."""
from typing import Any

from flask import current_app
from celery.schedules import crontab

from sqrl.extensions import celery, db


class SqlAlchemyTask(celery.Task):
    """A Celery task that ensures that the connection of the database is closed on task completion.
    """
    abstract = True

    def after_return(self, *args: Any, **kwargs: Any) -> None:
        """After each Celery task, teardown the database session."""
        db.session.remove()
    

@celery.task(base=SqlAlchemyTask)
def sync_data() -> None:
    """Sync the database with scraped data."""
    raise NotImplementedError
    

@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Any, **kwargs: Any) -> None:
    """Register periodic tasks with the celery beat scheduler."""
    # Get the schedule for the sync task, or make one to execute every hour if none is provided.
    sync_task_schedule = current_app.config.get('SYNC_TASK_SCHEDULE', dict(minute=0, hour='*/1'))
    sender.add_periodic_tasks(crontab(sync_task_schedule), sync_data.s(), name='sync_data')
