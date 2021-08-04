"A module containing dataset sources."
import re
import datetime
from dataclasses import dataclass
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Optional, Union

import requests
from bs4 import BeautifulSoup
from flask_mongoengine import MongoEngine

from sqrl import models
from sqrl.utils import nullable_convert, int_or_none


class DatasetSource(ABC):
    """An abstract class representing a dataset source."""
    # Private Instance Attributes:
    #   _db: The database session.
    _db: MongoEngine

    def __init__(self, db: MongoEngine) -> None:
        self._db = db

    @abstractmethod
    def sync(self, *args: Any, **kwargs: Any) -> None:
        """Pull data from the source and sync it with the database."""
        raise NotImplementedError


@dataclass
class TimetableSession:
    """A class representing a session of a calendar year.
    
    Instance Attributes:
        year: The year of the session.
        summer: Whether this is a summer session. Defaults to False, meaning that this is a
            fall/winter session.
    """
    year: int
    summer: bool = False
    
    @property
    def code(self) -> str:
        """
        Return the session code for this TimetableSession.
        
        The session code is a five-length string where the first four characters denote the session
        year, and the last character denotes whether it is a fall/winter (9) or summer session (5).
        For example, the code `20209` denotes the fall/winter session of 2020.

        >>> TimetableSession(2020, summer=False).code
        '20209'
        >>> TimetableSession(1966, summer=True).code
        '19665'
        >>> TimetableSession(1, summer=False).code
        00019
        """
        suffix = 5 if self.summer else 9
        return f'{self.year.zfill(4)}{suffix}'

    def __str__(self) -> str:
        return self.code

    @classmethod
    def parse(cls, session_code: str) -> 'TimetableSession':
        """Return an instance TimetableSession representing the given session code.
        Raise a ValueError if the session code is not formatted properly.

        >>> TimetableSession.parse('20205') == TimetableSession(2020, summer=True)
        True
        >>> TimetableSession.parse('20179') == TimetableSession(2017, summer=False)
        True
        """
        if len(session_code) != 5:
            raise ValueError(f'invalid session code ("{session_code}"): expected string of length 5'
                             f', not {len(session_code)}')
        elif not session_code.isnumeric():
            raise ValueError(f'invalid session code ("{session_code}"): expected numeric string')
        elif int(session_code[-1]) not in {9, 5}:
            raise ValueError(f'invalid session code ("{session_code}"): expected code to end in '
                             f'one of {{9, 5}}, not {session_code[-1]}')
        else:
            return TimetableSession(session_code[:4], session_code[-1] == 5)


class TimetableDatasetSource(DatasetSource):
    """A dataset source that contains information about course timetables.

    Instance Attributes:
        session_code: The session code. Defaults to None, meaning the latest (most up-to-date)
            session is used.
    """
    session: Optional[TimetableSession]

    def __init__(self, db: MongoEngine,
                 session: Optional[Union[TimetableSession, str]] = None) -> None:
        """Initialise an ArtsciTimetableAPI.
        
        Args:
            session: An optional session that can be supplied instead of the default.
                This can be an instance of TimetableSession or a string providing the session code.
        """
        super().__init__(db)
        if isinstance(session, str):
            self.session = TimetableSession.parse(session)
        elif session is None:
            self.session = self._get_latest_session()
        else:
            self.session = session

    def sync(self) -> None:
        """Pull course data from the Faculty of Arts and Science timetable API and sync it with
        the database."""
        # Sync courses
        courses = self._get_all_courses()
        for course in courses:
            self._sync_course(course)

    def _sync_course(self, course: models.Course) -> None:
        """Sync a sqrl.models.Course object."""
        # Sync sections
        for section in course.sections:
            self._sync_section(section)
        # Sync organisation
        course.organisation.save()
        # Sync course
        course.save()

    def _sync_section(self, section: models.Section) -> None:
        """Sync a sqrl.models.Section object."""
        # Nothing to do here!
        ...

    @abstractmethod
    def _get_all_courses(self) -> list[models.Course]:
        """Return all the courses in the session as a list of sqrl.models.Course objects."""
        raise NotImplementedError

    @abstractclassmethod
    def _get_latest_session(cls, verify: bool = False) -> TimetableSession:
        """Return the most up-to-date session from the timetable data source.
        Raise a ValueError if the session could not be found.
        
        Args:
            verify: Whether to verify the session code against the timetable. 
        """
        raise NotImplementedError


class UTSGTimetable(TimetableDatasetSource):
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
    # Private Instance Attributes
    #   _organisations: A dict mapping the code of each organisation in the Faculty of Arts
    #       and Science to its model object.
    _organisations: dict[str, models.Organisation]

    def __init__(self, db: MongoEngine,
                 session: Optional[Union[TimetableSession, str]] = None) -> None:
        super().__init__(db, session=session)
        self._organisations = {organisation.code: organisation
                               for organisation in self._get_all_organisations()}

    def _get_all_courses(self) -> list[models.Course]:
        """Return all the courses in the session as a list of sqrl.models.Course objects."""
        # Get courses for each department
        courses = []
        for organisation_code in self._organisations.keys():
            courses.extend(self._get_courses_in_organsisation(organisation_code))
        return courses

    def _get_courses_in_organsisation(self, organisation_code: str) -> list[models.Course]:
        """Return all the courses belonging to the given organisation as a list of
        sqrl.models.Course objects

        Args:
            organisation_code: The code of the organisation.
        """
        endpoint_url = f'{self.API_URL}/{self.session.code}/courses?org={organisation_code}'
        courses_dict = requests.get(endpoint_url).json() or {}
        return [self._parse_course(payload) for payload in courses_dict.values()]

    def _parse_course(self, payload: dict) -> models.Course:
        """Return an instance of sqrl.models.Course representing the course given by the payload."""
        # Full code is in the format <code>-<term>-<session>. For example, MAT137Y1-F-20219
        full_code = '{}-{}-{}'.format(payload['code'], payload['section'], payload['session'])
        return models.Course(
            id=full_code,
            organisation=self._organisations[payload['org']],
            code=payload['code'],
            title=payload['courseTitle'],
            description=payload['courseDescription'],
            term=models.CourseTerm(payload['section']),
            session_code=payload['session'],
            sections=[self._parse_section(x) for x in payload['meetings'].values()],
            prerequisites=payload['prerequisite'],
            corequisites=payload['corequisite'],
            exclusions=payload['exclusion'],
            recommended_preparation=payload['recommendedPreparation'],
            breadth_categories=payload['breadthCategories'],
            distribution_categories=payload['distributionCategories'],
            web_timetable_instructions=payload['webTimetableInstructions'],
            delivery_instructions=payload['deliveryInstructions'],
            campus=models.Campus.ST_GEORGE
        )

    def _parse_section(self, payload: dict) -> models.Section:
        """Return an instance of sqrl.models.Section representing the given payload."""
        # Parse instructors
        if (instructors := payload.get('instructors', [])) == []:
            # Replace empty list with empty dict for consistency
            instructors = {}
        instructors = [self._parse_instructor(x) for x in instructors.values()]
        # Parse meetings
        if (schedule := payload.get('schedule', [])) == []:
            # Replace empty list with empty dict for consistency
            schedule = {}
        meetings = self._parse_schedule(schedule)
        # Construct section object
        return models.Section(
            teaching_method=nullable_convert(payload.get('teachingMethod', None),
                                             models.SectionTeachingMethod),
            section_number=payload['sectionNumber'],
            subtitle=payload['subtitle'],
            instructors=instructors,
            meetings=meetings,
            delivery_mode=nullable_convert(payload.get('deliveryMode', None),
                                           models.SectionDeliveryMode),
            cancelled=payload.get('cancel', None) == 'Cancelled',
            has_waitlist=payload.get('waitlist', None) == 'Y',
            enrolment_capacity=int_or_none(payload.get('enrollmentCapacity', None)),
            actual_enrolment=int_or_none(payload.get('actualEnrolment', None)),
            actual_waitlist=int_or_none(payload.get('actualWaitlist', None)),
            enrolment_indicator=payload.get('enrollmentIndicator', None)
        )

    def _parse_instructor(self, payload: dict) -> models.Instructor:
        """Return an instance of sqrl.models.Instructor representing the given payload."""
        return models.Instructor(
            first_name=payload['firstName'],
            last_name=payload['lastName']
        )

    def _parse_schedule(self, payload: dict) -> list[models.SectionMeeting]:
        """Return a list of sqrl.models.SectionMeeting objects representing the given course
        meeting schedule payload.
        """
        meetings = []
        for meeting_data in payload.values():
            day = meeting_data.get('meetingDay', None)
            start_time = meeting_data.get('meetingStartTime', None)
            end_time = meeting_data.get('meetingEndTime', None)

            # Ignore meetings with a missing start/end time or day.
            if day is None or start_time is None or end_time is None:
                # NOTE: We should probably log this!
                continue

            meetings.append(models.SectionMeeting(
                day=models.MeetingDay(day),
                start_time=self._convert_time(start_time),
                end_time=self._convert_time(end_time),
                assigned_room_1=meeting_data.get('assignedRoom1', None),
                assigned_room_2=meeting_data.get('assignedRoom2', None)
            ))
        return meetings

    @classmethod
    def _get_all_organisations(cls) -> list[models.Organisation]:
        """Return a list of all the course departments in the Faculty of Arts and Science as a list
        of sqrl.models.Organisation objects. Raise a ValueError if the organisations could not be
        retrieved. Note that this does NOT mutate the database.
        """
        data = requests.get(f'{cls.API_URL}/orgs').json()
        if 'orgs' not in data:
            raise ValueError('could not get organisations: "orgs" key not found in response payload.')
        else:
            return [models.Organisation(code=code, name=name)
                    for code, name in data['orgs'].items()]

    @classmethod
    def _get_latest_session(cls, verify: bool = False) -> TimetableSession:
        """Return the session for the latest version of the Arts and Science timetable.
        Raise a ValueError if the session could not be found.

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
        
        return TimetableSession.parse(session_code)

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

    @staticmethod
    def _convert_time(time: str) -> models.Time:
        """Convert a length-5 time string in the format HH:MM using a 24-hour clock to a
        sqrl.models.Time object.

        >>> time = convert_time("08:30")
        >>> time.hour == 8 and time.minute == 30
        True
        >>> time = convert_time("11:00")
        >>> time.hour == 11 and time.minute == 0
        True
        """
        # Parts is a list consisting of two elements: hours and minutes.
        parts = [int(part) for part in time.split(':')]
        return models.Time(hour=parts[0], minute=parts[1])
