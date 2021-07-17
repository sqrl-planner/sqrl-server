"""Extensions attached onto the Flask app."""
from typing import Any

from celery import Celery
from flask.app import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate(db=db)
celery = Celery('sqrl', include=['sqrl.celery.tasks'])


def init_app(app: Flask) -> None:
    """Initialise extensions with a flask app context."""
    db.init_app(app)
    _init_migrate(app)


def init_celery(app: Flask) -> None:
    """Initialise the celery object instance with a flask app context."""
    celery.conf.update(
        app.config,
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        broker_url=app.config['CELERY_BROKER_URL']
    )

    class ContextTask(celery.Task):
        """A celery task that wraps the execution in a flask app context."""
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    return celery


def _init_migrate(app: Flask) -> None:
    """Initialise Flask Migrate with a flask app context."""
    is_sqlite = app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:')
    migrate.init_app(app, render_as_batch=is_sqlite)
