"""Celery worker module."""
from sqrl import create_app
from sqrl.extensions import init_celery


celery = init_celery(create_app())