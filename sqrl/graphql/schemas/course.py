"""Course query (proxy for gator API)."""
from types import SimpleNamespace
from typing import Any

import graphene
import mongoengine
from flask import current_app
from gator.models.timetable import Organisation, Course

from sqrl.extensions.gator_client import gator_client
from sqrl.graphql.objects.timetable import CourseObject, PaginatedCoursesObject, OrganisationObject, PaginatedOrganisationsObject


class CourseQuery(graphene.ObjectType):
    """A query in the graphql schema."""

    organisation_by_code = graphene.Field(
        OrganisationObject, code=graphene.String(required=True)
    )
    organisations = graphene.Field(PaginatedOrganisationsObject)

    courses_by_id = graphene.Field(
        PaginatedCoursesObject,
        ids=graphene.NonNull(graphene.List(graphene.NonNull(graphene.String)))
    )
    course_by_id = graphene.Field(
        CourseObject, id=graphene.String(required=True))
    courses = graphene.Field(PaginatedCoursesObject)
    # search_courses = graphene.List(
    #     CourseObject,
    #     query=graphene.String(required=True),
    #     offset=graphene.Int(required=False, default_value=0),
    #     limit=graphene.Int(required=False, default_value=25),
    # )

    def resolve_organisation_by_code(
        self, info: graphene.ResolveInfo, code: str
    ) -> Organisation:
        """Return an Organisation with the given code."""
        return gator_client.get_organisation(code)

    def resolve_organisations(
        self, info: graphene.ResolveInfo, **kwargs: Any
    ) -> SimpleNamespace:
        """Return a paginated list of Organisations."""
        return gator_client.get_organisations()

    def resolve_courses_by_id(
            self, info: graphene.ResolveInfo, ids: list[str]) -> list[Course]:
        """Return a paginated list of Courses filtered by the given ids."""
        return gator_client.get_courses(ids=ids)

    def resolve_course_by_id(
            self, info: graphene.ResolveInfo, id: str) -> Course:
        """Return a _CourseObject object with the given id."""
        return gator_client.get_course(id)

    def resolve_courses(self, info: graphene.ResolveInfo,
                        **kwargs: Any) -> list[Course]:
        """Return a list of _CourseObject objects."""
        gator_client.client._request('GET', '/courses/')
        return gator_client.get_courses()

    def resolve_search_courses(
        self, info: graphene.ResolveInfo, query: str, offset: int, limit: int
    ) -> list[Course]:
        """Return a list of _CourseObject objects matching the given search string."""
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
