import schedule

# Task configuration
# SYNC_TASK_SCHEDULE should be a schedule.Job class WITHOUT a func specified
SYNC_TASK_SCHEDULE = schedule.every().day.at('00:00')  # Execute every day at midnight