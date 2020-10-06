"""Scrape courses from the artsci timetable API."""

import re
import json
import argparse
import requests
from pathlib import Path
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

def is_session_code_valid(session_code):
    """Verifies a session code against the API.

    :returns:
        A boolean indicating whether the session code is valid.
    """

    # To verify the session code, we use it to find a course.
    # The session code is valid if the course is found.
    # We assume that MAT137 will be in all sessions (which is a reasonable
    # assumption to make seeing as it is required for many different majors,
    # and the recent rise in popularity of computer science).
    SEARCH_COURSE = 'MAT137'
    data = requests.get(f'{API_URL}/{session_code}/courses?code={SEARCH_COURSE}').json()
    return len(data) > 0

def get_session_code(verify=False):
    """Gets the current session code.

    The session code is a five-length string where the first four
    characters denote the session year, and the last character denotes
    whether it is a fall/winter (9) or summer session (5). For example,
    the code `20209` denotes the fall/winter session of 2020.

    :param verify:
        Whether to verify the session code. Defaults to False.
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

def get_orgs():
    """
    Gets all the departments (organisations).

    :returns:
        A mapping from organisation code to name.
    """

    data = requests.get(f'{API_URL}/orgs').json()
    if 'orgs' not in data:
        raise ValueError('Could not get organisations!')

    return data['orgs']

def _get_courses_in_org(org, session_code=None):
    """Gets all the courses belonging to the specified organisation.

    :param org:
        The organisation code.
    :param session_code:
        The session code. Defaults to None, meaning the current session
        (as returned by the `get_session_code` function).
    """

    return requests.get(f'{API_URL}/{session_code}/courses?org={org}').json()

def get_courses(session_code=None):
    """Gets all the courses.

    :param session_code:
        The session code. Defaults to None, meaning the current session
        (as returned by the `get_session_code` function).
    """

    # Get the session code (if unspecified)
    if session_code is None:
        session_code = get_session_code()

    # Get all the organisations
    orgs = get_orgs()
    courses = {}

    for org in orgs:
        org_courses = _get_courses_in_org(org, session_code)
        if len(org_courses) == 0: continue

        for course_name in org_courses:
            if course_name in courses: continue
            courses[course_name] = org_courses[course_name]

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