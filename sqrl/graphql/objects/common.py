"""GraphQL objects for common models."""
from graphene_mongo import MongoengineObjectType

from gator.models.common import Time


class TimeObject(MongoengineObjectType):
    """A time object in the graphql schema."""

    class Meta:
        model = Time
