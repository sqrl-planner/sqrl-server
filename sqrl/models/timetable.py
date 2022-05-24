"""Model data classes for timetable."""
import re
import math
import secrets
from enum import Enum
from typing import Optional
from functools import lru_cache

import petname

from sqrl.extensions import db
from sqrl.models.common import Time


class MeetingDay(Enum):
    """A class representing the day of the week."""

    MONDAY = 'MO'
    TUESDAY = 'TU'
    WEDNESDAY = 'WE'
    THURSDAY = 'TH'
    FRIDAY = 'FR'
    SATURDAY = 'SA'
    SUNDAY = 'SU'


class SectionMeeting(db.EmbeddedDocument):
    """A class representing a meeting of a section.

    Instance Attributes:
        day: The day of this meeting.
        start_time: The start time of this meeting.
        end_time: The end time of this meeting.
        assigned_room_1: A string representing the first assigned room for this
            meeting, or None if there is no first assigned room.
        assigned_room_2: A string representing the second assigned room for
            this meeting, or None if there is no second assigned room.
    """

    day: MeetingDay = db.EnumField(MeetingDay, required=True)
    start_time: Time = db.EmbeddedDocumentField(Time, required=True)
    end_time: Time = db.EmbeddedDocumentField(Time, required=True)
    assigned_room_1: Optional[str] = db.StringField(null=True)
    assigned_room_2: Optional[str] = db.StringField(null=True)


class SectionTeachingMethod(Enum):
    """A class representing the teaching method for a section."""

    LECTURE = 'LEC'
    TUTORIAL = 'TUT'
    PRACTICAL = 'PRA'


class SectionDeliveryMode(Enum):
    """A class representing mode of delivery for a section."""

    CLASS = 'CLASS'
    ONLINE_SYNC = 'ONLSYNC'
    ONLINE_ASYNC = 'ONLASYNC'
    IN_PERSON = 'INPER'
    SYNC = 'SYNC'
    ASYNC = 'ASYNC'
    # idk why they keep changing delivery modes
    ASYIF = 'ASYIF'
    SYNIF = 'SYNIF'


class Instructor(db.EmbeddedDocument):
    """A class representing a course instructor.

    Instance Attributes:
        id: A unique integer id representing this instructor.
        first_name: The first name of this instructor.
        last_name: The last name of this instructor.
    """

    first_name: str = db.StringField(required=True)
    last_name: str = db.StringField(required=True)


class Section(db.EmbeddedDocument):
    """A class representing a course section/meeting.

    Instance Attributes:
        teaching_method: The teaching method for this section, or None if this
            section has no teaching method.
        section_number: The number of this section, representing as a string.
        subtitle: The section subtitle, or None if there is no subtitle.
        instructors: A list of instructors teaching this section.
        meetings: A list of meetings available for this section.
        delivery_mode: The delivery mode for this section, or None if this
            section has no delivery mode.
        cancelled: Whether this section is cancelled.
        has_waitlist: Whether this section has a waitlist.
        enrolment_capacity: The total number of students that can be enrolled
            in this section.
        actual_enrolment: The number of students enrolled in this section.
        actual_waitlist: The number of students waitlisted for this section.
        enrolment_indicator: A string representing the enrollment indicator
            for this section, or None if there is no enrollment indicator.
    """

    teaching_method: Optional[SectionTeachingMethod] = db.EnumField(
        SectionTeachingMethod, null=True
    )
    section_number: str = db.StringField()
    subtitle: Optional[str] = db.StringField(null=True)
    instructors: list[Instructor] = db.EmbeddedDocumentListField('Instructor')
    meetings: list[SectionMeeting] = db.EmbeddedDocumentListField(
        'SectionMeeting')
    delivery_mode: Optional[SectionDeliveryMode] = db.EnumField(
        SectionDeliveryMode, null=True)
    cancelled: bool = db.BooleanField()
    has_waitlist: bool = db.BooleanField()
    enrolment_capacity: Optional[int] = db.IntField(null=True)
    actual_enrolment: Optional[int] = db.IntField(null=True)
    actual_waitlist: Optional[int] = db.IntField(null=True)
    enrolment_indicator: Optional[str] = db.StringField(null=True)

    @property
    def code(self) -> str:
        """Return a string representing the code of this section. This is a
        combination of the teaching method and the section number, separated
        by a hyphen.
        """
        return f'{self.teaching_method.value}-{self.section_number}'


class CourseTerm(Enum):
    """The course term."""

    FIRST_SEMESTER = 'F'
    SECOND_SEMESTER = 'S'
    FULL_YEAR = 'Y'


class Campus(Enum):
    """University campus"""

    ST_GEORGE = 'UTSG'
    SCARBOROUGH = 'UTSC'
    MISSISSAUGA = 'UTM'


class Organisation(db.Document):
    """
    A class representing a department (which offers courses).

    Instance Attributes:
        code: A unique string representing this organisation.
        name: The full name of this organisation.
    """

    code: str = db.StringField(primary_key=True)
    name: str = db.StringField(required=True)


class Course(db.Document):
    """A class representing a course.

    Instance Attributes:
        id: The full code of the course.
            Formatted as "{code}-{term}-{session_code}".
        organisation: The Organisation that this course is associated with.
        code: The course code.
        title: The title of this course.
        description: The description of this course.
        term: The term in which the course takes place.
        session_code: The session in which the course takes place represented as a 5 character
            numeric string.
        sections: A list of sections available for this course.
        prerequisites: Prerequisties for this course.
        corequisites: Corequisites for this course.
        exclusions: Exclusions for this course.
        recommended_preparation: Recommended preparations to complete before this course.
        breadth_categories: The breadth categories this course can fulfill.
        distribution_categories: The distribution categories this course can fulfill.
        web_timetable_instructions: Additional timetable information.
        delivery_instructions: Additional delivery instruction information.
    """

    id: str = db.StringField(primary_key=True)
    organisation: Organisation = db.ReferenceField('Organisation')
    code: str = db.StringField()
    title: str = db.StringField()
    description: str = db.StringField()
    term: CourseTerm = db.EnumField(CourseTerm)
    session_code: str = db.StringField(min_length=5, max_length=5)
    sections: list[Section] = db.EmbeddedDocumentListField('Section')
    prerequisites: str = db.StringField()  # TODO: Parse this
    corequisites: str = db.StringField()  # TODO: Parse this
    exclusions: str = db.StringField()  # TODO: Parse this
    recommended_preparation: str = db.StringField()
    breadth_categories: str = db.StringField()  # TODO: Parse this
    distribution_categories: str = db.StringField()  # TODO: Parse this
    web_timetable_instructions: str = db.StringField()
    delivery_instructions: str = db.StringField()
    campus: Campus = db.EnumField(Campus, required=True)

    meta = {
        'indexes': [
            {
                'fields': ['$title', '$description'],
                'default_language': 'english',
                'weights': {'title': 1.5, 'description': 1},
            }
        ]
    }

    @property
    @lru_cache
    def section_codes(self) -> set[str]:
        """Return a set of section codes for this course."""
        return {section.code for section in self.sections}

    @property
    @lru_cache
    def level(self) -> int:
        """Return the level of this course."""
        m = re.search(r'(?:[^\d]*)(\d+)', self.code)
        return int(math.floor(int(m.group(1)) / 100.0)) * 100

    def __str__(self):
        """Return a string representation of this course."""
        return f'{self.code}: {self.title}'


def _generate_timetable_name() -> str:
    """Generates a name for a timetable."""
    return petname.Generate()


class Timetable(db.Document):
    """A class representing a timetable.

    Instance Attributes:
        key: The auth key for this timetable.
        meetings: A mapping of course codes to list of section meetings selected for that course.
    """

    name: str = db.StringField(default=_generate_timetable_name)
    key: str = db.StringField(required=True, default=secrets.token_urlsafe)
    sections: dict[str, list[str]] = db.MapField(
        db.ListField(db.StringField()), default=dict)
