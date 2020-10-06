"""Custom commands used with the Flask CLI."""

import click
from pathlib import Path
from flask.cli import with_appcontext

from sqrl.extensions import db

def init_app(app):
    """Initializes click commands with an app context."""
    app.cli.add_command(_init_db_command)

@click.command('init-db')
@with_appcontext
def _init_db_command():
    """Recreates the database."""
    confirmation = click.confirm('Are you sure you would like to continue? This will drop and recreate all tables in the database.')
    if confirmation:
        db.drop_all()
        db.create_all()
        click.echo('Initialized the database: dropped and recreated all tables.')