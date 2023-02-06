"""Model data classes for timetable."""
import secrets

import petname

from sqrl.extensions import db


class UserTimetable(db.Document):
    """A class representing a user's timetable.

    Instance Attributes:
        key: The auth key for this timetable.
        meetings: A mapping of course codes to list of section meetings selected for that course.
        sections: A mapping of course codes to a list of sections for that course.
        deleted: Whether this timetable has been deleted.
    """

    name: str = db.StringField(default=petname.Generate)
    key: str = db.StringField(required=True, default=secrets.token_urlsafe)
    sections: dict[str, list[str]] = db.MapField(
        db.ListField(db.StringField()), default=dict)
    deleted: bool = db.BooleanField(default=False)
