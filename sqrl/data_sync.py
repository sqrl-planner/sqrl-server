"""Syncs data from the timetable API."""

import json
import tqdm
import datetime
from sqrl import models
from sqrl.utils import to_int
from sqrl.extensions import db

def convert_time_str(time_str):
    """Convert a length-5 string in the format HH:MM using a
    24-hour clock to a datetime.time object.

    >>> result = datetime.time(hour=8, minute=30)
    >>> result == convert_time_str("08:30")
    True
    >>> result = datetime.time(hour=11, minute=0)
    >>> result == convert_time_str("11:00")
    True
    """
    # Parts is a list consisting of two elements: hours and minutes.
    parts = [int(part) for part in time_str.split(':')]
    return datetime.time(parts[0], parts[1])

def convert_instructor(instructor_data):
    """Convert JSON instructor data to a :class:`sqrl.models.Instructor`."""
    instructor_id = int(instructor_data['instructorId'])
    instructor = models.Instructor.query.filter_by(
        id=instructor_id
    ).first()

    if instructor is None:
        instructor = models.Instructor(id=instructor_id)
        db.session.add(instructor)

    instructor.first_name = instructor_data['firstName']
    instructor.last_name = instructor_data['lastName']

    db.session.flush()
    return instructor

def convert_instructors(instructors_data):
    """Convert JSON instructors data to a list of :class:`sqrl.models.Instructor` objects."""
    if len(instructors_data) == 0: return list()
    return [convert_instructor(x) for x in instructors_data.values()]

def convert_meetings(meetings_data):
    """Convert JSON meetings data to a list of :class:`sqrl.models.SectionMeeting` objects."""
    if len(meetings_data) == 0: return list()

    meetings = []
    for meeting_data in meetings_data.values():
        day = meeting_data.get('meetingDay', None)
        start_time = meeting_data.get('meetingStartTime', None)
        end_time = meeting_data.get('meetingEndTime', None)

        # Ignore meetings with a missing start/end time or day.
        if day is None or start_time is None or end_time is None:
            continue

        meeting_id = int(meeting_data['meetingScheduleId'])
        meeting = models.SectionMeeting.query.filter_by(
            id=meeting_id
        ).first()
        if meeting is None:
            meeting = models.SectionMeeting(
                id=meeting_id,
                day=models.MeetingDay(day),
                start_time=convert_time_str(start_time),
                end_time=convert_time_str(end_time),
                assigned_room_1=meeting_data.get('assignedRoom1', None),
                assigned_room_2=meeting_data.get('assignedRoom2', None)
            )

            db.session.add(meeting)
        else:
            meeting.day = models.MeetingDay(day)
            meeting.start_time = convert_time_str(start_time)
            meeting.end_time = convert_time_str(end_time)
            meeting.assigned_room_1 = meeting_data.get('assignedRoom1', None)
            meeting.assigned_room_2 = meeting_data.get('assignedRoom2', None)

        db.session.flush()

        meetings.append(meeting)

    return meetings

def _to_section_teaching_method(value):
    """Convert a string to a :class:`sqrl.models.SectionTeachingMethod`."""
    if value is None: return None
    return models.SectionTeachingMethod(value)

def _to_section_delivery_mode(value):
    """Convert a string to a :class:`sqrl.models.SectionDeliveryMode`."""
    if value is None: return None
    return models.SectionDeliveryMode(value)

def convert_section(section_data):
    """Convert JSON section data to a :class:`sqrl.models.Section`."""
    section_id = int(section_data['meetingId'])
    section = models.Section.query.filter_by(
        id=section_id
    ).first()

    if section is None:
        section = models.Section(id=section_id)
        db.session.add(section)

    section.teaching_method = _to_section_teaching_method(section_data.get('teachingMethod', None))
    section.section_number = section_data['sectionNumber']
    section.subtitle = section_data['subtitle']
    section.instructors = convert_instructors(section_data['instructors'])
    section.meetings = convert_meetings(section_data['schedule'])

    section.delivery_mode = _to_section_delivery_mode(section_data.get('deliveryMode', None))
    section.online = section_data.get('online', None)
    section.cancelled = section_data.get('cancel', None) == 'Cancelled'

    section.has_waitlist = section_data.get('waitlist', None) == 'Y'
    section.enrolment_capacity = to_int(section_data.get('enrollmentCapacity', None))
    section.actual_enrolment = to_int(section_data.get('actualEnrolment', None))
    section.actual_waitlist = to_int(section_data.get('actualWaitlist', None))
    section.enrollmentIndicator = section_data.get('enrollmentIndicator', None)

    db.session.flush()
    return section

def convert_sections(sections_data):
    """Convert JSON sections data to a list of :class:`sqrl.models.Section` objects."""
    return [convert_section(x) for x in sections_data.values()]

def convert_organisation(code, name):
    """Gets an organisation, or creates it if it doesn't exist.

    :param code:
        A unique string representing the organisation.
    :param name:
        The full name of the organisation.
    """
    organisation = models.Organisation.query.filter_by(
        code=code
    ).first()

    if organisation is None:
        organisation = models.Organisation(code=code)
        db.session.add(organisation)

    organisation.name = name

    db.session.flush()
    return organisation

def convert_course(course_data):
    """Convert JSON course data to a :class:`sqrl.models.Course`."""
    course_id = int(course_data['courseId'])
    course = models.Course.query.filter_by(
        id=course_id
    ).first()

    if course is None:
        course = models.Course(id=course_id)
        db.session.add(course)

    # Update columns
    course.organisation = convert_organisation(
        course_data['org'],
        course_data['orgName']
    )

    course.code = course_data['code']
    course.title = course_data['courseTitle']
    course.description = course_data['courseDescription']

    course.term = models.CourseTerm(course_data['section'])
    course.session = course_data['session']
    course.sections = convert_sections(course_data['meetings'])

    course.prerequisite = course_data['prerequisite']
    course.corequisite = course_data['corequisite']
    course.exclusion = course_data['exclusion']
    course.recommended_preparation = course_data['recommendedPreparation']
    course.breadth_categories = course_data['breadthCategories']
    course.distribution_categories = course_data['distributionCategories']

    course.web_timetable_instructions = course_data['webTimetableInstructions']
    course.delivery_instructions = course_data['deliveryInstructions']

    db.session.flush()
    return course

def sync_from_file(filepath):
    """
    Syncs course data from a JSON file.

    The data should be in the raw format provided
    by the UofT timetable API.
    """

    with open(filepath) as file:
        courses_data = json.load(file)

    import time

    start_time = time.time()
    for course_data in tqdm.tqdm(courses_data.values()):
        convert_course(course_data)

    elapsed_seconds = time.time() - start_time
    print('Converting {} courses took {:.2f} seconds ({:.2f} seconds/course)'.format(
        len(courses_data), elapsed_seconds, elapsed_seconds / len(courses_data)
    ))

    start_time = time.time()
    db.session.commit()
    print('Writing to database took {:.2f} seconds'.format(time.time() - start_time))
