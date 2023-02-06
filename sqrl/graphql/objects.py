"""GraphQL objects for timetable models."""
from typing import Any

import graphene
from gator.core.models.common import Time
from gator.core.models.timetable import (Course, Instructor, Organisation,
                                         Section, SectionMeeting)
from graphene_mongo import MongoengineObjectType

from sqrl.models import UserTimetable


class TimeObject(MongoengineObjectType):
    """A time object in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = Time


class SectionMeetingObject(MongoengineObjectType):
    """A section meeting in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = SectionMeeting


class InstructorObject(MongoengineObjectType):
    """An instructor in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = Instructor


class SectionObject(MongoengineObjectType):
    """A section in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = Section

    code = graphene.String()

    def resolve_code(self, info: graphene.ResolveInfo, **kwargs: Any) -> str:
        """Resolve the code of the section."""
        return self.code


class OrganisationObject(MongoengineObjectType):
    """An organisation in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = Organisation


class PaginatedOrganisationsObject(graphene.ObjectType):
    """A paginated list of organisations in the graphql schema."""

    organisations = graphene.List(OrganisationObject)
    last_id = graphene.String()


class CourseObject(MongoengineObjectType):
    """A course in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = Course


class PaginatedCoursesObject(graphene.ObjectType):
    """A paginated list of courses in the graphql schema."""

    courses = graphene.List(CourseObject)
    last_id = graphene.String()


class UserTimetableObject(MongoengineObjectType):
    """A timetable in the graphql schema."""

    class Meta:
        """Meta class for the TimeObject."""
        model = UserTimetable
        exclude_fields = ('key',)
