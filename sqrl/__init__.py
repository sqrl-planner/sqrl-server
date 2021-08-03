"""Entrypoint for the Flask app."""
import mimetypes
from pathlib import Path
from typing import Union, Any

from flask import Flask


def create_app(instance_config_filename: Union[str, Path] = 'local_config.py',
               test_config: Any = None) -> Flask:
    """Creates the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('sqrl.config')
    if test_config is None:
        app.config.from_pyfile(instance_config_filename, silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    # from sqrl import routes, models, cli
    from sqrl import extensions, models, cli
    extensions.init_app(app)
    # routes.init_app(app)
    cli.init_app(app)

    # Register mimetypes
    mimetypes.add_type('text/css', '.css')
    mimetypes.add_type('text/javascript', '.js')

    return app
    