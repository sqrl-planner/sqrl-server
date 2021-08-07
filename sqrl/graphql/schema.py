from typing import Any
import graphene
from graphene_mongo import MongoengineObjectType

from sqrl.models import Organisation, Course
    

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
