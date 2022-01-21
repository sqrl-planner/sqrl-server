import schedule

from sqrl.data.sources import utsg as utsg_source

# Dataset configuration
DATASET_SOURCES = {
    'utsg-timetable': utsg_source.UTSG_ArtsSci_TimetableDatasetSource(session=None),
}

# Task configuration
# NOTE: SYNC_TASK_SCHEDULE should be a schedule.Job class WITHOUT a func specified
SYNC_TASK_SCHEDULE = schedule.every().day.at('00:00')  # Execute every day at midnight