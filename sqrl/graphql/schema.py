from typing import Any, Optional

import graphene
from graphene_mongo import MongoengineObjectType

from sqrl.models.common import Time
from sqrl.models.timetable import (
    SectionMeeting,
    Instructor,
    Section,
    Organisation,
    Course
)
    

class _TimeObject(MongoengineObjectType):
    """A time object in the graphql schema."""
    class Meta:
        model = Time


class _SectionMeetingObject(MongoengineObjectType):
    """A section meeting in the graphql schema."""
    class Meta:
        model = SectionMeeting


class _InstructorObject(MongoengineObjectType):
    """An instructor in the graphql schema."""
    class Meta:
        model = Instructor


class _SectionObject(MongoengineObjectType):
    """A section in the graphql schema."""
    class Meta:
        model = Section


class _OrganisationObject(MongoengineObjectType):
    """An organisation in the graphql schema."""
    class Meta:
        model = Organisation


class _OrganisationObjectConnection(graphene.relay.Connection):
    """A connection for the Organisation object."""
    class Meta:
        node = _OrganisationObject


class _CourseObject(MongoengineObjectType):
    """A course in the graphql schema."""
    class Meta:
        model = Course


class _CourseObjectConnection(graphene.relay.Connection):
    """A connection for the Course object."""
    class Meta:
        node = _CourseObject


class Query(graphene.ObjectType):
    """A query in the graphql schema."""
    organisation_by_code = graphene.Field(_OrganisationObject, code=graphene.String(required=True))
    organisations = graphene.ConnectionField(_OrganisationObjectConnection)

    course_by_id = graphene.Field(_CourseObject, id=graphene.String(required=True))
    courses = graphene.ConnectionField(_CourseObjectConnection)
    search_courses = graphene.List(_CourseObject,
                                   query=graphene.String(required=True),
                                   offset=graphene.Int(required=False, default_value=0),
                                   limit=graphene.Int(required=False, default_value=25))

    def resolve_organisation_by_code(self, info: Any, code: str) -> Organisation:
        """Return an _OrganisationObject object with the given code."""
        return Organisation.objects.get(code=code)

    def resolve_organisations(self, info: Any, **kwargs: Any) -> list[Organisation]:
        """Return a list of _OrganisationObject objects."""
        return list(Organisation.objects.all())

    def resolve_course_by_id(self, info: Any, id: str) -> Course:
        """Return a _CourseObject object with the given id."""
        return Course.objects.get(id=id)

    def resolve_courses(self, info: Any, **kwargs: Any) -> list[Course]:
        """Return a list of _CourseObject objects."""
        return list(Course.objects.all())

    def resolve_search_courses(self, info: Any, query: str, offset: int, limit: int) \
            -> list[Course]:
        """Return a list of _CourseObject objects matching the given search string."""
        return list(Course.objects[offset:offset+limit])

schema = graphene.Schema(query=Query)
