"""Database migration extension."""
from flask import Flask
from flask_migrate import Migrate
from sqrl.extensions.db import db

migrate = Migrate(db=db)


def init_app(app: Flask) -> None:
    """Initialise Flask Migrate with a flask app context."""
    is_sqlite = app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:')
    migrate.init_app(app, render_as_batch=is_sqlite)
