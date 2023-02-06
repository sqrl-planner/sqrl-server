"""Entrypoint for the Flask app."""
from typing import Any

from flask import Flask
from werkzeug.debug import DebuggedApplication
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(settings_override: Any = None) -> Flask:
    """Create a Flask application using the app factory pattern.

    Args:
        settings_override: Override settings

    Returns:
        A Flask application instance.
    """
    app = Flask(__name__, static_folder='../public', static_url_path="")
    app.config.from_object('config.app_settings')
    if settings_override:
        app.config.update(settings_override)

    init_middleware(app)

    from sqrl import graphql
    graphql.init_app(app)

    import sqrl.extensions as extensions
    extensions.init_app(app)

    return app


def init_middleware(app: Flask) -> None:
    """Register 0 or more middleware (mutates the app passed in).

    Args:
        app: A Flask application instance.
    """
    # Enable the Flask interactive debugger in the browser for development.
    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # Set the real IP address into request.remote_addr when behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return None
