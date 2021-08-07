from flask import Flask
from flask_graphql import GraphQLView

from sqrl.graphql.schema import schema


def init_app(app: Flask) -> None:
    """Initialise GraphQL with a flask app context."""
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )
