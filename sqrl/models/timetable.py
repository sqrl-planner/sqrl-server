"""Model data classes for timetable."""
from enum import Enum
from datetime import datetime
from typing import List, Optional

from sqrl.extensions import db


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
        assigned_room_1: A string representing the first assigned room for this meeting, or None
            if there is no first assigned room.
        assigned_room_2: A string representing the second assigned room for this meeting, or None
            if there is no second assigned room.
    """
    day: MeetingDay = db.EnumField(MeetingDay, required=True)
    start_time: datetime = db.DateTimeField(required=True)
    end_time: datetime = db.DateTimeField(required=True)
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


class Instructor(db.Document):
    """A class representing a course instructor.
    
    Instance Attributes:
        id: A unique integer id representing this instructor as returned by the API.
        first_name: The first name of this instructor.
        last_name: The last name of this instructor.
    """
    id: int = db.IntField(primary_key=True, unique=True, required=True)
    first_name: str = db.StringField(required=True)
    last_name: str = db.StringField(required=True)


class Section(db.EmbeddedDocument):
    """A class representing a course section/meeting.
    
    Instance Attributes:
        teaching_method: The teaching method for this section, or None if this section has no
            teaching method.
        section_number: The number of this section, representing as a string.
        subtitle: The section subtitle, or None if there is no subtitle.
        instructors: A list of instructors teaching this section.
        meetings: A list of meetings available for this section.
        delivery_mode: The delivery mode for this section, or None if this section has no delivery
            mode.
        cancelled: Whether this section is cancelled.
        has_waitlist: Whether this section has a waitlist.
        enrollment_capacity: The total number of students that can be enrolled in this section.
        actual_enrolment: The number of students enrolled in this section.
        actual_waitlist: The number of students waitlisted for this section.
        enrollment_indicator: A string representing the enrollment indicator for this section,
            or None if there is no enrollment indicator.
    """
    teaching_method: SectionTeachingMethod = db.EnumField(SectionTeachingMethod)
    section_number: str = db.StringField()
    subtitle: Optional[str] = db.StringField(null=True)
    instructors: List[Instructor] = db.ListField(db.ReferenceField('Instructor'))
    meetings: List[SectionMeeting] = db.EmbeddedDocumentListField('SectionMeeting')
    delivery_mode: SectionDeliveryMode = db.EnumField(SectionDeliveryMode)
    cancelled: bool = db.BooleanField()
    has_waitlist: bool = db.BooleanField()
    enrollment_capacity: Optional[int] = db.IntField(null=True)
    actual_enrolment: Optional[int] = db.IntField(null=True)
    actual_waitlist: Optional[int] = db.IntField(null=True)
    enrolment_indicator: Optional[str] = db.StringField(null=True)


class CourseTerm(Enum):
    """The course term."""
    FIRST_SEMESTER = 'F'
    SECOND_SEMESTER = 'S'
    FULL_YEAR = 'Y'


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
        organisation: The Organisation that this course is associated with.
        code: The course code.
        title: The title of this course.
        description: The description of this course.
        term: The term in which the course takes place.
        session: The session in which the course takes place.
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
    id: str = db.StringField(primary_key=True, unique=True, required=True)
    organisation: Organisation = db.ReferenceField('Organisation')
    code: str = db.StringField()
    title: str = db.StringField()
    description: str = db.StringField()
    term: CourseTerm = db.EnumField(CourseTerm)
    session: str = db.StringField(min_length=5, max_length=5)
    sections: List[Section] = db.EmbeddedDocumentListField('Section')
    prerequisites: str = db.StringField()  # TODO: Parse this
    corequisites: str = db.StringField()  # TODO: Parse this
    exclusions: str = db.StringField()  # TODO: Parse this
    recommended_preparation: str = db.StringField()
    breadth_categories: str = db.StringField()  # TODO: Parse this
    distribution_categories: str = db.StringField()  # TODO: Parse this
    web_timetable_instructions: str = db.StringField()
    delivery_instructions: str = db.StringField()
