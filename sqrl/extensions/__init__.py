"""Extensions attached onto the Flask app."""
from flask import Flask

from sqrl.extensions.db import init_app as _init_db, db  # noqa: F401
from sqrl.extensions.cors import init_app as _init_cors


def init_app(app: Flask) -> None:
    """Initialise extensions with a flask app context."""
    _init_db(app)
    _init_cors(app)
