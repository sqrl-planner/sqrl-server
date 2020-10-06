"""Model data classes for timetable."""

from enum import Enum
from sqrl.extensions import db

class Organisation(db.Model):
    """
    A model representing a department (which offers courses).

    :ivar id:
        A unique integer id representing the organisation.
    :ivar code:
        A unique string representing the organisation.
    :ivar name:
        The full name of the organisation.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, index=True)
    name = db.Column(db.Text)

class SectionTeachingMethod(Enum):
    """Teaching method of the section."""
    LECTURE = 'LEC'
    TUTORIAL = 'TUT'
    PRACTICAL = 'PRA'

class SectionDeliveryMode(Enum):
    """Delivery mode of the section."""
    CLASS = 'CLASS'
    ONLINE_SYNC = 'ONLSYNC'
    ONLINE_ASYNC = 'ONLASYNC'

class MeetingDay(Enum):
    """Day of the week."""
    MONDAY = 'MO'
    TUESDAY = 'TU'
    WEDNESDAY = 'WE'
    THURSDAY = 'TH'
    FRIDAY = 'FR'
    SATURDAY = 'SA'
    SUNDAY = 'SU'

class Instructor(db.Model):
    """A model representing a course instructor."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)

# An association table mapping sections to their instructors.
instructors_sections = db.Table(
    'instructor_section_association',
    db.Column('section_id', db.Integer, db.ForeignKey('section.id')),
    db.Column('instructor_id', db.Integer, db.ForeignKey('instructor.id'))
)

class SectionMeetingTime(db.Model):
    """A model representing a meeting time of a section."""
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Enum(MeetingDay))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    assigned_room_1 = db.Column(db.Text)
    assigned_room_2 = db.Column(db.Text)

    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship('Section', back_populates='meetings')

class Section(db.Model):
    """A model representing a course section/meeting."""
    id = db.Column(db.Integer, primary_key=True)
    teaching_method = db.Column(db.Enum(SectionTeachingMethod))
    section_number = db.Column(db.String(32))
    subtitle = db.Column(db.Text)
    instructors = db.relationship(
        'Instructor',
        secondary=instructors_sections
    )

    meetings = db.relationship(
        'SectionMeetingTime',
        back_populates='section'
    )

    delivery_mode = db.Column(db.Enum(SectionDeliveryMode))
    online = db.Column(db.Text)
    cancelled = db.Column(db.Boolean)

    has_waitlist = db.Column(db.Boolean)
    enrolment_capacity = db.Column(db.Integer)
    actual_enrolment = db.Column(db.Integer)
    actual_waitlist = db.Column(db.Integer)
    enrolment_indicator = db.Column(db.String(32))

class CourseTerm(Enum):
    """The course term."""
    FIRST_SEMESTER = 'F'
    SECOND_SEMESTER = 'S'
    FULL_YEAR = 'Y'

class Course(db.Model):
    """A model representing a course in the timetable."""
    id = db.Column(db.Integer, primary_key=True)

    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    organisation = db.relationship('Organisation')

    code = db.Column(db.String(32), index=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)

    section = db.Column(db.Enum(CourseTerm))
    session = db.Column(db.String(5), index=True)

    prerequisite = db.Column(db.Text)
    corequisite = db.Column(db.Text)
    exclusion = db.Column(db.Text)
    recommended_preparation = db.Column(db.Text)
    breadth_categories = db.Column(db.Text)
    distribution_categories = db.Column(db.Text)

    web_timetable_instructions = db.Column(db.Text)
    delivery_instructions = db.Column(db.Text)
