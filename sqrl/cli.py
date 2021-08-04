"""Custom commands used with the Flask CLI."""
import time

import click
from flask.app import Flask
from flask.cli import with_appcontext

from sqrl.extensions import db
from sqrl.data.sources import UTSGTimetable


def init_app(app: Flask) -> None:
    """Initializes click commands with an app context."""
    app.cli.add_command(_sync_command)


@click.command('sync')
@with_appcontext
def _sync_command() -> None:
    """Sync database with data scraped from UofT APIs."""
    confirmation = click.confirm('Are you sure you would like to continue? This cannot be undone!')
    if confirmation:
        sources = [UTSGTimetable(db)]
        for source in sources:
            start_time = time.time()
            source.sync()
            elapsed = time.time() - start_time
            click.echo(f'Synced data from {source.__class__.__name__}! Took {elapsed:.2f} seconds')