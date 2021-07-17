"""Model data classes for timetable."""
import datetime
from enum import Enum
from typing import Optional, List

from sqrl.extensions import db


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


class MeetingDay(Enum):
    """A class representing the day of the week."""
    MONDAY = 'MO'
    TUESDAY = 'TU'
    WEDNESDAY = 'WE'
    THURSDAY = 'TH'
    FRIDAY = 'FR'
    SATURDAY = 'SA'
    SUNDAY = 'SU'


class Organisation(db.Model):
    """
    A class representing a department (which offers courses).

    Instance Attributes:
        id: A unique integer id representing this organisation.
        code: A unique string representing this organisation.
        name: The full name of this organisation.
    """
    id: int = db.Column(db.Integer, primary_key=True)
    code: str = db.Column(db.String(32), unique=True, index=True)
    name: str = db.Column(db.Text)


class Instructor(db.Model):
    """A class representing a course instructor.
    
    Instance Attributes:
        id: A unique integer id representing this instructor.
        first_name: The first name of this instructor.
        last_name: The last name of this instructor.
    """
    id: int = db.Column(db.Integer, primary_key=True)
    first_name: str = db.Column(db.Text)
    last_name: str = db.Column(db.Text)


class SectionMeeting(db.Model):
    """A class representing a meeting of a section.

    Instance Attributes:
        id: A unique integer id representing this meeting.
        day: The day of this meeting.
        start_time: The start time of this meeting.
        end_time: The end time of this meeting.
        assigned_room_1: A string representing the first assigned room for this meeting, or None
            if there is no first assigned room.
        assigned_room_2: A string representing the second assigned room for this meeting, or None
            if there is no second assigned room.
        section_id: The id of the Section that this meeting is associated with.
        section: The Section that this meeting is associated with.
    """
    id: int = db.Column(db.Integer, primary_key=True)
    day: MeetingDay = db.Column(db.Enum(MeetingDay))
    start_time: datetime.time = db.Column(db.Time)
    end_time: datetime.time = db.Column(db.Time)
    assigned_room_1: Optional[str] = db.Column(db.Text, nullable=True)
    assigned_room_2: Optional[str] = db.Column(db.Text, nullable=True)
    section_id: int = db.Column(db.Integer, db.ForeignKey('section.id'))
    section: 'Section' = db.relationship('Section', back_populates='meetings')


# An association table mapping sections to their instructors.
instructors_sections = db.Table(
    'instructor_section_association',
    db.Column('section_id', db.Integer, db.ForeignKey('section.id')),
    db.Column('instructor_id', db.Integer, db.ForeignKey('instructor.id'))
)


class Section(db.Model):
    """A class representing a course section/meeting.
    
    Instance Attributes:
        id: A unique integer id representing this section.
        course_id: The id of the course that this section is associated with.
        course: The Course that this section is associated with.
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
    id = db.Column(db.Integer, primary_key=True)
    course_id: int = db.Column(db.Integer, db.ForeignKey('course.id'))
    course: 'Course' = db.relationship('Course', back_populates='sections')
    teaching_method: Optional[SectionTeachingMethod] = db.Column(db.Enum(SectionTeachingMethod),
                                                                 nullable=True)
    section_number: str = db.Column(db.String(32))
    subtitle: Optional[str] = db.Column(db.Text, nullable=True)
    instructors: List[Instructor] = db.relationship('Instructor', secondary=instructors_sections)
    meetings: List[SectionMeeting] = db.relationship( 'SectionMeeting', back_populates='section')
    delivery_mode: Optional[SectionDeliveryMode] = db.Column(db.Enum(SectionDeliveryMode),
                                                             nullable=True)
    cancelled: bool = db.Column(db.Boolean)
    has_waitlist: bool = db.Column(db.Boolean)
    enrollment_capacity: int = db.Column(db.Integer)
    actual_enrolment: int = db.Column(db.Integer)
    actual_waitlist: int = db.Column(db.Integer)
    enrolment_indicator: Optional[str] = db.Column(db.String(32), nullable=True)


class CourseTerm(Enum):
    """The course term."""
    FIRST_SEMESTER = 'F'
    SECOND_SEMESTER = 'S'
    FULL_YEAR = 'Y'


class Course(db.Model):
    """A class representing a course.
    
    Instance Attributes:
        id: A unique integer id representing this course.
        organisation_id: The id of the organisation that this course is associated with.
        organisation: The Organisation that this course is associated with.
        code: The course code.
        title: The title of this course.
        description: The description of this course.
        term: The term in which the course takes place.
        session: The session in which the course takes place.
        sections: A list of sections available for this course.
        prerequisite: Prerequisties for this course.
        corequisite: Corequisites for this course.
        exclusion: Exclusions for this course.
        recommended_preparation: Recommended preparations to complete before this course.
        breadth_categories: The breadth categories this course can fulfill.
        distribution_categories: The distribution categories this course can fulfill.
        web_timetable_instructions: Additional timetable information.
        delivery_instructions: Additional delivery instruction information.
    """
    id: int = db.Column(db.Integer, primary_key=True)
    organisation_id: int = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    organisation: Organisation = db.relationship('Organisation')
    code: str = db.Column(db.String(32), index=True)
    title: str = db.Column(db.Text)
    description: str = db.Column(db.Text)
    term: CourseTerm = db.Column(db.Enum(CourseTerm))
    session: str = db.Column(db.String(5), index=True)
    sections: List[Section] = db.relationship('Section', back_populates='course')
    prerequisite: str = db.Column(db.Text)  # TODO: Parse this
    corequisite: str = db.Column(db.Text)  # TODO: Parse this
    exclusion: str = db.Column(db.Text)  # TODO: Parse this
    recommended_preparation: str = db.Column(db.Text)
    breadth_categories: str = db.Column(db.Text)  # TODO: Parse this
    distribution_categories: str = db.Column(db.Text)  # TODO: Parse this
    web_timetable_instructions: str = db.Column(db.Text)
    delivery_instructions: str = db.Column(db.Text)