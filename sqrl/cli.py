"""Custom commands used with the Flask CLI."""

import click
from pathlib import Path
from flask.cli import with_appcontext

from sqrl.extensions import db
from sqrl.data_sync import sync_from_file

def init_app(app):
    """Initializes click commands with an app context."""
    app.cli.add_command(_init_db_command)
    app.cli.add_command(_load_courses_command)

@click.command('init-db')
@with_appcontext
def _init_db_command():
    """Recreates the database."""
    confirmation = click.confirm('Are you sure you would like to continue? This will drop and recreate all tables in the database.')
    if confirmation:
        db.drop_all()
        db.create_all()
        click.echo('Initialized the database: dropped and recreated all tables.')

@click.command('load-courses')
@click.argument('courses_json_filepath', type=Path)
@with_appcontext
def _load_courses_command(courses_json_filepath):
    """Loads courses from a JSON file."""
    confirmation = click.confirm('Are you sure you would like to continue? This cannot be undone!')
    if confirmation:
        sync_from_file(courses_json_filepath)
        click.echo(f'Loaded data from \'{courses_json_filepath.resolve()}\'')