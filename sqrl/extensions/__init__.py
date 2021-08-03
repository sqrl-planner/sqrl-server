"""Extensions attached onto the Flask app."""
from flask import Flask

from sqrl.extensions.db import db, init_app as _init_db


def init_app(app: Flask) -> None:
    """Initialise extensions with a flask app context."""
    _init_db(app)
    