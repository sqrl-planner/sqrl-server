"""A worker that pulls data from remote APIs and syncs it with local database."""
import time

import schedule
from flask import Flask

from sqrl import create_app
from sqrl.extensions import db


def _sync_job(app: Flask) -> None:
    """A job that syncs data from remote APIs and local database."""
    dataset_sources = app.config.get('DATASET_SOURCES', {})
    print(f'Syncing data from ({len(dataset_sources)}) dataset sources')
    print('-' * 80)
    for source_name, source in dataset_sources.items():
        print(f'* Syncing {source_name}...', end='', flush=True)
        start_time = time.time()
        source.sync(db)
        print(f'Finished syncing {source_name} in {time.time() - start_time:.2f} seconds')


if __name__ == '__main__':
    app = create_app()
    
    # Get the schedule for the sync task, or make one to execute every day if none is provided.
    DEFAULT_SYNC_TASK_SCHEDULE = schedule.every().day.at('00:00')
    sync_task_schedule = app.config.get('SYNC_TASK_SCHEDULE', DEFAULT_SYNC_TASK_SCHEDULE)
    if not isinstance(sync_task_schedule, schedule.Job):
        raise ValueError('expected SYNC_TASK_SCHEDULE to be an instance of schedule.Job, not '
                        f'{sync_task_schedule.__class__.__name__}')
    sync_task_schedule.do(lambda: _sync_job(app))
    
    # Run the schedule loop
    while True:
        schedule.run_pending()
        time.sleep(1)
