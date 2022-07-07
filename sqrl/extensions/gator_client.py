"""Gator client extension."""
from typing import Optional, Any

from flask import Flask
from gator.api.client import GatorClient


class FlaskGatorClient:
    """Thin wrapper around GatorClient to allow for configuration through
    Flask app.
    """
    app: Optional[Flask]
    client: GatorClient

    def __init__(self, app: Optional[Flask] = None) -> None:
        """Initialise the Gator client."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialise the Gator client with a Flask app context."""
        self.app = app

        base_url = app.config.get('GATOR_CLIENT_URL', None)
        if base_url is None:
            raise ValueError('GATOR_CLIENT_URL not set')

        self.client = GatorClient(
            base_url,
            encoding=app.config.get('GATOR_CLIENT_ENCODING', 'utf-8')
        )

    def __getattr__(self, attr: str) -> Any:
        """A proxy attribute getter for the Gator client this
        extension wraps."""
        return getattr(self.client, attr)


gator_client = FlaskGatorClient()
