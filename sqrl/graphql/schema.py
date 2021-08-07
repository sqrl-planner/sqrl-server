from typing import Any
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


class _CourseObject(MongoengineObjectType):
    """A course in the graphql schema."""
    class Meta:
        model = Course


class Query(graphene.ObjectType):
    """A query in the graphql schema."""
    organisations = graphene.List(_OrganisationObject)
    courses = graphene.List(_CourseObject)

    def resolve_organisations(self, info: Any) -> Any:
        """Return a list of _OrganisationObject objects."""
        return list(Organisation.objects.all())

    def resolve_courses(self, info: Any) -> Any:
        """Return a list of _CourseObject objects."""
        return list(Course.objects.all())


schema = graphene.Schema(query=Query)
