"""Extension enabling supprot for CORS."""
from flask import Flask
from flask_cors import CORS

cors = CORS()


def init_app(app: Flask) -> None:
    """Initialise Flask-CORS with a flask app context."""
    cors.init_app(app)
