"""Course query (proxy for gator API)."""
from typing import Any

import graphene
import mongoengine
from flask import current_app
from gator.models.timetable import Organisation, Course

from sqrl.graphql.objects.timetable import CourseObject, OrganisationObject


class CourseQuery(graphene.ObjectType):
    """A query in the graphql schema."""

    organisation_by_code = graphene.Field(
        OrganisationObject, code=graphene.String(required=True)
    )
    # organisations = graphene.ConnectionField(_OrganisationObjectConnection)

    courses_by_id = graphene.List(
        CourseObject,
        ids=graphene.NonNull(graphene.List(graphene.NonNull(graphene.String))))
    course_by_id = graphene.Field(
        CourseObject, id=graphene.String(required=True))
    # courses = graphene.ConnectionField(_CourseObjectConnection)
    search_courses = graphene.List(
        CourseObject,
        query=graphene.String(required=True),
        offset=graphene.Int(required=False, default_value=0),
        limit=graphene.Int(required=False, default_value=25),
    )

    def resolve_organisation_by_code(
        self, info: graphene.ResolveInfo, code: str
    ) -> Organisation:
        """Return an _OrganisationObject object with the given code."""
        return Organisation.objects.get(code=code)

    def resolve_organisations(
        self, info: graphene.ResolveInfo, **kwargs: Any
    ) -> list[Organisation]:
        """Return a list of _OrganisationObject objects."""
        return list(Organisation.objects.all())

    def resolve_courses_by_id(
            self, info: graphene.ResolveInfo, ids: list[str]) -> list[Course]:
        """Return a list of _CourseObject objects, each with given ids.
        Courses that do not exist are null.
        """
        courses = []
        for id in ids:
            try:
                course = Course.objects.get(id=id)
                courses.append(course)
            except mongoengine.DoesNotExist:
                courses.append(None)
        return courses

    def resolve_course_by_id(
            self, info: graphene.ResolveInfo, id: str) -> Course:
        """Return a _CourseObject object with the given id."""
        return Course.objects.get(id=id)

    def resolve_courses(self, info: graphene.ResolveInfo,
                        **kwargs: Any) -> list[Course]:
        """Return a list of _CourseObject objects."""
        return list(Course.objects.all())

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
