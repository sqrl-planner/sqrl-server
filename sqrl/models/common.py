"""Common models."""
from sqrl.extensions.db import db


class Time(db.EmbeddedDocument):
    """A class representing an HH:MM time in 24-hour format."""

    hour: int = db.IntField(min_value=0, max_value=23, required=True)
    minute: int = db.IntField(min_value=0, max_value=59, required=True)
