"""Scrape courses from the artsci timetable API."""
import re
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict

from bs4 import BeautifulSoup


ROOT_URL = 'https://timetable.iit.artsci.utoronto.ca'
API_URL = f'{ROOT_URL}/api'


DEFAULT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    # Emulate Gecko agent
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


def is_session_code_valid(session_code: str) -> bool:
    """Verifies a session code against the API. Return whether the session code is valid."""
    # To verify the session code, we use it to find a course.
    # The session code is valid if the course is found.
    # We assume that MAT137 will be in all sessions (which is a reasonable
    # assumption to make seeing as it is required for many different majors,
    # and the recent rise in popularity of computer science).
    SEARCH_COURSE = 'MAT137'
    data = requests.get(f'{API_URL}/{session_code}/courses?code={SEARCH_COURSE}').json()
    return len(data) > 0


def get_session_code(verify: bool = False) -> str:
    """Return the current session code.
    
    The session code is a five-length string where the first four characters denote the session
    year, and the last character denotes whether it is a fall/winter (9) or summer session (5).
    For example, the code `20209` denotes the fall/winter session of 2020.

    Args:
        verify: Whether to verify the session code against the API. 
    """
    request = requests.get(ROOT_URL, DEFAULT_HEADERS)
    soup = BeautifulSoup(request.content, 'html.parser')

    # The search button contains the session code
    search_button = soup.find('input', {'id': 'searchButton', 'class': 'btnSearch'})

    SESSION_CODE_PATTERN = r'(?<=searchCourses\(\')\d{5}(?=\'\))'
    matches = re.findall(SESSION_CODE_PATTERN, search_button['onclick'])
    if len(matches) == 0:
        raise ValueError('Failed to find session code!')

    session_code = matches[0]
    if verify and not is_session_code_valid(session_code):
        raise ValueError('Failed to find session code!')
    
    return session_code


def get_organisations() -> Dict[str, str]:
    """Return a dict mapping the code of all the organisations at UofT to its name.
    Raise a ValueError if the organisations could not be retrieved.
    """
    data = requests.get(f'{API_URL}/orgs').json()
    if 'orgs' not in data:
        raise ValueError('could not get organisations! "orgs" key not found in response payload.')
    else:
        return data['orgs']


def _get_courses_in_organsisation(organisation_code: str, session_code: Optional[str] = None) \
        -> dict:
    """Return all the courses belonging to the specified organisation as a dict mapping each course
    code to its json data.

    Args:
        organisation_code: The code of the organisation.
        session_code: The session code. Defaults to None, meaning the current session is used
            (as returned by the `get_session_code` function).
    """
    return requests.get(f'{API_URL}/{session_code}/courses?org={organisation_code}').json()


def get_courses(session_code: Optional[str] = None) -> dict:
    """Return all the courses for the current session as a dict mapping each course code to its
    json data.

    Args:
        session_code: The session code. Defaults to None, meaning the current session is used
            (as returned by the `get_session_code` function).
    """
    # Get the session code (if unspecified)
    if session_code is None:
        session_code = get_session_code()

    # Get all the organisations
    organisations = get_organisations()
    courses = {}
    for organisation_code in organisations:
        organsation_courses = _get_courses_in_organsisation(organisation_code, session_code)
        if len(organsation_courses) == 0: continue

        for course_name in organsation_courses:
            if course_name in courses:
                # Skip duplicates
                # TODO: We might want to log this as a warning!
                continue
            courses[course_name] = organsation_courses[course_name]

    return courses


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape courses from the artsci timetable API.')
    parser.add_argument('output_filepath', type=Path, help='Where to save the scraped data.')
    parser.add_argument('--format-json', help='Format the JSON file.', action='store_true')
    parser.set_defaults(format_json=None)
    args = parser.parse_args()

    args.output_filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_filepath, 'w+') as output_file:
        json.dump(get_courses(), output_file, indent=args.format_json)
    