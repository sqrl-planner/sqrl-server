import graphene

from sqrl.graphql.schemas.course import CourseQuery
from sqrl.graphql.schemas.timetable import TimetableQuery, TimetableMutation

ALL_QUERIES = [CourseQuery, TimetableQuery]
ALL_MUTATIONS = [TimetableMutation]

# NOTE: To add a new query schema, make AppQuery inherit from your custom
# Query class or add it to the list of ALL_QUERIES.
class AppQuery(*ALL_QUERIES, graphene.ObjectType):
    """All queries for the gator app."""

# NOTE: To add a new mutation schema, make AppMutation inherit from your
# custom Mutation class or add it to the list of ALL_MUTATIONS.
class AppMutation(*ALL_MUTATIONS, graphene.ObjectType):
    """All mutations for the gator app."""


app_schema = graphene.Schema(query=AppQuery, mutation=AppMutation)
