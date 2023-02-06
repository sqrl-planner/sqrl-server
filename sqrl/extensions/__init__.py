"""Flask extensions."""
from flask import Flask

from sqrl.extensions.cors import cors
from sqrl.extensions.db import db
from sqrl.extensions.gator_client import gator_client


def init_app(app: Flask) -> None:
    """Initialise the Flask extensions."""
    cors.init_app(app)
    db.init_app(app)
    gator_client.init_app(app)
