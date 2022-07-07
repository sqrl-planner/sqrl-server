from flask import Flask
from graphql_server.flask import GraphQLView

from sqrl.graphql.schemas import app_schema


def init_app(app: Flask) -> None:
    """Initialise GraphQL with a flask app context."""
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=app_schema.graphql_schema,
            graphiql=True),
    )
