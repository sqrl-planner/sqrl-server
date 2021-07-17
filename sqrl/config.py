SQLALCHEMY_TRACK_MODIFICATIONS = False

# Task configuration
# SYNC_TASK_SCHEDULE should be a dict specifying keyword arguments to the
# celery.schedules.crontab function.
SYNC_TASK_SCHEDULE = dict(minute=0, hour='*/1')  # Execute every hour: midnight, 1am, 2am, etc...