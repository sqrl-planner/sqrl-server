"A module containing dataset sources."
import re
from dataclasses import dataclass
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Optional, Union

from flask_mongoengine import MongoEngine

from sqrl import models


class DatasetSource(ABC):
    """An abstract class representing a dataset source."""
    @abstractmethod
    def sync(self, db: MongoEngine, *args: Any, **kwargs: Any) -> None:
        """Pull data from the source and sync it with the database.
        
        Args:
            db: The database session.
        """
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

    def __init__(self,
                 session: Optional[Union[TimetableSession, str]] = None) -> None:
        """Initialise an ArtsciTimetableAPI.
        
        Args:
            session: An optional session that can be supplied instead of the default.
                This can be an instance of TimetableSession or a string providing the session code.
        """
        super().__init__()
        if isinstance(session, str):
            self.session = TimetableSession.parse(session)
        elif session is None:
            self.session = self._get_latest_session()
        else:
            self.session = session

    def sync(self, db: MongoEngine) -> None:
        """Pull course data from the Faculty of Arts and Science timetable API and sync it with
        the database."""
        # Sync courses
        courses = self._get_all_courses()
        for course in courses:
            self._sync_course(course, db)

    def _sync_course(self, course: models.Course, _: MongoEngine) -> None:
        """Sync a sqrl.models.Course object."""
        # Sync organisation
        course.organisation.save()
        # Sync course
        course.save()

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
