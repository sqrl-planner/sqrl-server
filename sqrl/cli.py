"""Custom commands used with the Flask CLI."""
import time

import click
from flask.app import Flask
from flask.cli import with_appcontext

from sqrl.data.sources import UTSGTimetable
from sqrl.extensions import db


def init_app(app: Flask) -> None:
    """Initializes click commands with an app context."""
    app.cli.add_command(_init_db_command)
    app.cli.add_command(_sync_datasets)


@click.command('init-db') 
@with_appcontext
def _init_db_command() -> None:
    """Recreates the database."""
    confirmation = click.confirm('Are you sure you would like to continue? This will drop and recreate all tables in the database.')
    if confirmation:
        db.drop_all()
        db.create_all()
        click.echo('Initialized the database: dropped and recreated all tables.')


@click.command('sync-datasets')
@with_appcontext
def _sync_datasets() -> None:
    """Sync database with data scraped from UofT APIs."""
    confirmation = click.confirm('Are you sure you would like to continue? This cannot be undone!')
    if confirmation:
        sources = [UTSGTimetable(db)]
        for source in sources:
            start_time = time.time()
            source.pull_and_sync()
            elapsed = time.time() - start_time
            click.echo(f'Synced data from {source.__class__.__name__}! Took {elapsed:.2f} seconds')
        