"""GraphQL extension for flask."""
from flask import Flask

from graphql_server.flask import GraphQLView
from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLString
)

schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'hello': GraphQLField(
                GraphQLString,
                resolve=lambda obj, info: 'world')
        }
    )
)


def init_app(app: Flask):
    """Initialise GraphQL views given a flask app context."""
    app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    ))
