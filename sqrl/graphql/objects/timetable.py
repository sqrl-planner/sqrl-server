"""GraphQL objects for timetable models."""
from typing import Any

import graphene
from graphene_mongo import MongoengineObjectType

from gator.models.timetable import (Course, Instructor, Organisation, Section,
                                    SectionMeeting)

from sqrl.models import UserTimetable


class SectionMeetingObject(MongoengineObjectType):
    """A section meeting in the graphql schema."""

    class Meta:
        model = SectionMeeting


class InstructorObject(MongoengineObjectType):
    """An instructor in the graphql schema."""

    class Meta:
        model = Instructor


class SectionObject(MongoengineObjectType):
    """A section in the graphql schema."""

    class Meta:
        model = Section

    code = graphene.String()

    def resolve_code(self, info: graphene.ResolveInfo, **kwargs: Any) -> str:
        """Resolve the code of the section."""
        return self.code


class OrganisationObject(MongoengineObjectType):
    """An organisation in the graphql schema."""

    class Meta:
        model = Organisation


class CourseObject(MongoengineObjectType):
    """A course in the graphql schema."""

    class Meta:
        model = Course


class UserTimetableObject(MongoengineObjectType):
    """A timetable in the graphql schema."""

    class Meta:
        model = UserTimetable
        exclude_fields = ('key',)
