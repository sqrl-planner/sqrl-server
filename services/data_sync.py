"""A worker that pulls data from remote APIs and syncs it with local database."""
import time
from datetime import datetime

import schedule

from sqrl import create_app


def _sync_job():
    print('syncing')
    print(datetime.now().strftime("%H:%M:%S"))


if __name__ == '__main__':
    app = create_app()
    
    # Get the schedule for the sync task, or make one to execute every day if none is provided.
    DEFAULT_SYNC_TASK_SCHEDULE = schedule.every().day.at('00:00')
    sync_task_schedule = app.config.get('SYNC_TASK_SCHEDULE', DEFAULT_SYNC_TASK_SCHEDULE)
    if not isinstance(sync_task_schedule, schedule.Job):
        raise ValueError('expected SYNC_TASK_SCHEDULE to be an instance of schedule.Job, not '
                        f'{sync_task_schedule.__class__.__name__}')
    sync_task_schedule.do(_sync_job)
    
    # Run the schedule loop
    while True:
        schedule.run_pending()
        time.sleep(1)
