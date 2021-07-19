"A module containing dataset sources."
import re
import datetime
from typing import Any, Optional
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy, Model

from sqrl import models
from sqrl.utils import nullable_convert, int_or_none


class DatasetSource(ABC):
    """An abstract class representing a dataset source."""
    # Private Instance Attributes:
    #   _db: The database session.
    _db: SQLAlchemy

    def __init__(self, db: SQLAlchemy) -> None:
        self._db = db

    @abstractmethod
    def scrape_and_sync(self, *args: Any, **kwargs: Any) -> None:
        """Scrape data from the source, and merge it into the database."""
        raise NotImplementedError


class UTSGTimetable(DatasetSource):
    """A dataset source implementation for the St. George campus Arts and Science timetable API.
    
    Class Attributes:
        ROOT_URL: The root url for the API homepage.
        API_URL: The url for the API root endpoint.
        DEFAULT_HEADERS: A dict containing default headers used for API requests.

    Instance Attributes:
        session_code: The session code. Defaults to None, meaning the current session is used
            (as returned by the `sqrl.data.sources.ArtsciTimetableAPI.get_session_code` method).
    """
    ROOT_URL: str = 'https://timetable.iit.artsci.utoronto.ca'
    API_URL: str = f'{ROOT_URL}/api'
    DEFAULT_HEADERS: dict = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        # Emulate Gecko agent
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    session_code: Optional[str]

    def __init__(self, db: SQLAlchemy, session_code: Optional[str] = None) -> None:
        """Initialise an ArtsciTimetableAPI.
        
        Args:
            session_code: An optional session code that can be supplied instead of the default.
        """
        super().__init__(db)
        if session_code is None:
            self.session_code = self._get_session_code()
        else:
            self.session_code = session_code

    def scrape_and_sync(self) -> None:
        """Scrape course data from the Faculty of Arts and Science timetable, convert it to
        sqrl.models objects, and merge it into the database."""
        for course_data in self._get_all_courses():
            self._sync_course(course_data)

        self._db.commit()
        
    def _get_all_courses(self) -> list[dict]:
        """Return all the courses in the session."""
        organisations = self._get_organisations()
        return [
            course for organisation_code in organisations
            for course in self._get_courses_in_organsisation(organisation_code)
        ]

    def _get_courses_in_organsisation(self, organisation_code: str) -> dict[str, dict]:
        """Return all the courses belonging to the specified organisation as a dict mapping each course
        code to its json data.

        Args:
            organisation_code: The code of the organisation.
        """
        endpoint_url = f'{self.API_URL}/{self.session_code}/courses?org={organisation_code}'
        return requests.get(endpoint_url).json() or {}

    @classmethod
    def _get_organisations(cls) -> dict[str, str]:
        """Return a dict mapping the code of all the organisations at UofT to its name.
        Raise a ValueError if the organisations could not be retrieved.
        """
        data = requests.get(f'{cls.API_URL}/orgs').json()
        if 'orgs' not in data:
            raise ValueError('could not get organisations! "orgs" key not found in response payload.')
        else:
            return data['orgs']

    @classmethod
    def _get_session_code(cls, verify: bool = False) -> str:
        """Return the current session code. Raise a ValueError if the session could not be found.
        
        The session code is a five-length string where the first four characters denote the session
        year, and the last character denotes whether it is a fall/winter (9) or summer session (5).
        For example, the code `20209` denotes the fall/winter session of 2020.

        Args:
            verify: Whether to verify the session code against the API. 
        """
        request = requests.get(cls.ROOT_URL, cls.DEFAULT_HEADERS)
        soup = BeautifulSoup(request.content, 'html.parser')

        # The search button contains the session code
        search_button = soup.find('input', {'id': 'searchButton', 'class': 'btnSearch'})

        SESSION_CODE_PATTERN = r'(?<=searchCourses\(\')\d{5}(?=\'\))'
        matches = re.findall(SESSION_CODE_PATTERN, search_button['onclick'])
        if len(matches) == 0:
            raise ValueError('failed to find session code!')

        session_code = matches[0]
        if verify and not cls._is_session_code_valid(session_code):
            raise ValueError('failed to find session code!')
        
        return session_code

    @classmethod
    def _is_session_code_valid(cls, session_code: str) -> bool:
        """Verifies a session code against the API. Return whether the session code is valid."""
        # To verify the session code, we use it to find a course. The session code is valid if the
        # course is found. We assume that MAT137 will be in all sessions (which is a reasonable
        # assumption since it is a required course for a variety of majors, including computer science,
        # which has only been rising in popularity in the past few decades).
        SEARCH_COURSE = 'MAT137'
        data = requests.get(f'{cls.API_URL}/{session_code}/courses?code={SEARCH_COURSE}').json()
        return len(data) > 0

    def _sync_course(self, course_data: dict) -> models.Course:
        """Add or update a course given a dict containing json course data in the format given by
        the timetable API."""
        course_id = int(course_data['courseId'])
        course = models.Course.query.filter_by(id=course_id).first()
        if course is None:
            # Create course object
            course = models.Course(id=course_id)
            self._db.session.add(course)

        # Update course attributes
        course.organisation = self._sync_organisation(course_data['org'], course_data['orgName'])
        course.code = course_data['code']
        course.title = course_data['courseTitle']
        course.description = course_data['courseDescription']
        course.term = models.CourseTerm(course_data['section'])
        course.session = course_data['session']
        course.sections = [
            self._sync_section(section) for section in course_data['meetings'].values()
        ]
        course.prerequisites = course_data['prerequisite']
        course.corequisites = course_data['corequisite']
        course.exclusions = course_data['exclusion']
        course.recommended_preparation = course_data['recommendedPreparation']
        course.breadth_categories = course_data['breadthCategories']
        course.distribution_categories = course_data['distributionCategories']
        course.web_timetable_instructions = course_data['webTimetableInstructions']
        course.delivery_instructions = course_data['deliveryInstructions']
        
        self._db.session.flush()
        return course

    def _sync_organisation(self, code: str, name: str) -> models.Organisation:
        """Add or update an organisation given its code and name in the database. Return a
        sqrl.models.Organisation object."""
        organisation = models.Organisation.query.filter_by(code=code).first()
        if organisation is None:
            organisation = models.Organisation(code=code)
            self._db.session.add(organisation)

        organisation.name = name
        self._db.session.flush()
        return organisation

    def _sync_section(self, section_data: dict) -> models.Section:
        """Add or update a course section given a dict containing json course data in the format
        given by the timetable API."""
        section_id = int(section_data['meetingId'])
        section = models.Section.query.filter_by(id=section_id).first()
        if section is None:
            section = models.Section(id=section_id)
            self._db.session.add(section)

        section.teaching_method = nullable_convert(
            section_data.get('teachingMethod', None),
            models.SectionTeachingMethod.__init__
        )    
        section.section_number = section_data['sectionNumber']
        section.subtitle = section_data['subtitle']
        section.instructors = [
            self._sync_instructor(instructor_data) for instructor_data in
            section_data['instructors'].values()
        ]
        section.meetings = self._sync_section_meeting(section_data['schedule'])

        section.delivery_mode = nullable_convert(
            section_data.get('deliveryMode', None),
            models.SectionDeliveryMode.__init__
        )
        section.online = section_data.get('online', None)
        section.cancelled = section_data.get('cancel', None) == 'Cancelled'

        section.has_waitlist = section_data.get('waitlist', None) == 'Y'
        section.enrolment_capacity = int_or_none(section_data.get('enrollmentCapacity', None))
        section.actual_enrolment = int_or_none(section_data.get('actualEnrolment', None))
        section.actual_waitlist = int_or_none(section_data.get('actualWaitlist', None))
        section.enrollmentIndicator = section_data.get('enrollmentIndicator', None)

        self._db.session.flush()
        return section

    def _sync_instructor(self, instructor_data: dict) -> models.Instructor:
        """Add or update a course instructor given a dict containing json instructor data in the
        format given by the timetable API."""
        instructor_id = int(instructor_data['instructorId'])
        instructor = models.Instructor.query.filter_by(
            id=instructor_id
        ).first()

        if instructor is None:
            instructor = models.Instructor(id=instructor_id)
            self._db.session.add(instructor)

        instructor.first_name = instructor_data['firstName']
        instructor.last_name = instructor_data['lastName']

        self._db.session.flush()
        return instructor

    def _sync_section_meetings(self, section_meetings_data: dict) -> list[models.SectionMeeting]:
        """Add or update a course section meeting given a dict containing section meetings
        in the format given by the timetable API."""
        meetings = []
        for meeting_data in section_meetings_data.values():
            day = meeting_data.get('meetingDay', None)
            start_time = meeting_data.get('meetingStartTime', None)
            end_time = meeting_data.get('meetingEndTime', None)

            # Ignore meetings with a missing start/end time or day.
            if day is None or start_time is None or end_time is None:
                # NOTE: We should probably log this!
                continue

            meeting_id = int(meeting_data['meetingScheduleId'])
            meeting = models.SectionMeeting.query.filter_by(
                id=meeting_id
            ).first()
            if meeting is None:
                meeting = models.SectionMeeting(
                    id=meeting_id,
                    day=models.MeetingDay(day),
                    start_time=self._convert_time(start_time),
                    end_time=self._convert_time(end_time),
                    assigned_room_1=meeting_data.get('assignedRoom1', None),
                    assigned_room_2=meeting_data.get('assignedRoom2', None)
                )
                self._db.session.add(meeting)
            else:
                meeting.day = models.MeetingDay(day)
                meeting.start_time = self._convert_time(start_time)
                meeting.end_time = self._convert_time(end_time)
                meeting.assigned_room_1 = meeting_data.get('assignedRoom1', None)
                meeting.assigned_room_2 = meeting_data.get('assignedRoom2', None)

            self._db.session.flush()
            meetings.append(meeting)

        return meeting

    @staticmethod
    def _convert_time(time: str) -> datetime.time:
        """Convert a length-5 time string in the format HH:MM using a 24-hour clock to a
        datetime.time object.

        >>> result = datetime.time(hour=8, minute=30)
        >>> result == convert_time("08:30")
        True
        >>> result = datetime.time(hour=11, minute=0)
        >>> result == convert_time("11:00")
        True
        """
        # Parts is a list consisting of two elements: hours and minutes.
        parts = [int(part) for part in time.split(':')]
        return datetime.time(parts[0], parts[1])
