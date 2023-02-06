"""Course query (proxied from Gator API)."""
from types import SimpleNamespace
from typing import Optional

import graphene
from flask import current_app
from gator.core.models.timetable import Course

from sqrl.extensions import gator_client
from sqrl.graphql.objects import CourseObject, PaginatedCoursesObject


class CourseQuery(graphene.ObjectType):
    """Course related queries."""

    courses_by_id = graphene.Field(
        PaginatedCoursesObject,
        ids=graphene.NonNull(graphene.List(graphene.NonNull(graphene.String)))
    )
    course_by_id = graphene.Field(
        CourseObject, id=graphene.String(required=True))
    courses = graphene.Field(
        PaginatedCoursesObject,
        page_size=graphene.Int(default_value=None),
        last_id=graphene.String(default_value=None),
    )
    # search_courses = graphene.List(
    #     CourseObject,
    #     query=graphene.String(required=True),
    #     offset=graphene.Int(required=False, default_value=0),
    #     limit=graphene.Int(required=False, default_value=25),
    # )

    def resolve_courses_by_id(
            self, info: graphene.ResolveInfo, ids: list[str]) -> list[Course]:
        """Return a paginated list of Courses filtered by the given ids."""
        return gator_client.get_courses(ids=ids)

    def resolve_course_by_id(
            self, info: graphene.ResolveInfo, id: str) -> Course:
        """Return a _CourseObject object with the given id."""
        return gator_client.get_course(id)

    def resolve_courses(self, info: graphene.ResolveInfo,
                        page_size: Optional[int] = None,
                        last_id: Optional[str] = None) -> SimpleNamespace:
        """Return a list of _CourseObject objects."""
        gator_client.client._request('GET', '/courses/')
        return gator_client.get_courses(page_size=page_size, last_id=last_id)

    def resolve_search_courses(
        self, info: graphene.ResolveInfo, query: str, offset: int, limit: int
    ) -> list[Course]:
        """Return a list of Courses matching the given search string."""
        # log search query
        # TODO: Add improved logging
        current_app.logger.info(f'searchCourses - query: "{query}", '
                                f'offset: {offset}, limit: {limit}')

        courses_code = Course.objects(code__icontains=query)
        # First n search results
        n = courses_code.count()
        if offset < n:
            courses = list(courses_code[offset: offset + limit])
            if limit > n - offset:
                courses_text = Course.objects.search_text(
                    query).order_by('$text_score')
                courses += list(courses_text.limit(limit - n + offset))
            return courses
        else:
            courses = Course.objects.search_text(query).order_by('$text_score')
            offset -= n
            return list(courses[offset: offset + limit])
