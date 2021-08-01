"""SQLAlchemy database extension."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app: Flask) -> None:
    """Initialise database with a flask app context."""
    db.init_app(app)
