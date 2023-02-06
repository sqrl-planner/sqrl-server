"""GraphQL integration for the Sqrl flask app."""
from flask import Flask
from graphql.validation.rules.custom.no_schema_introspection import \
    NoSchemaIntrospectionCustomRule
from graphql.validation.specified_rules import specified_rules
from graphql_server.flask import GraphQLView

from sqrl.graphql.schemas import app_schema


def init_app(app: Flask) -> None:
    """Initialise GraphQL with a flask app context."""
    on_dev = app.config.get('DEBUG', False)
    prod_rules = specified_rules + tuple([NoSchemaIntrospectionCustomRule])
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=app_schema.graphql_schema,
            validation_rules=None if on_dev else prod_rules,
            graphiql=on_dev,
        )
    )
