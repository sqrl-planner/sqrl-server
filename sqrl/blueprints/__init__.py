"""All blueprints for Sqrl server."""
from flask import Flask

from sqrl.blueprints import ping


def register(app: Flask) -> None:
    """Register blueprints to the given Flask app."""
    app.register_blueprint(ping.bp)
