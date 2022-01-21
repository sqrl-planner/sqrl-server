"""Custom commands used with the Flask CLI."""
import time

import click
from flask import Flask, current_app
from flask.cli import with_appcontext

from sqrl.extensions import db


def init_app(app: Flask) -> None:
    """Initializes click commands with an app context."""
    app.cli.add_command(_sync_command)


@click.command('sync')
@click.option('--yes', '-y', is_flag=True, default=False,
              help='Skip confirmation prompt')
@with_appcontext
def _sync_command(yes: bool) -> None:
    """Sync database with data."""
    if not yes:
        confirmation = click.confirm(
            'Are you sure you would like to continue? This cannot be undone!'
        )
    else:
        confirmation = True

    if confirmation:
        dataset_sources = current_app.config.get('DATASET_SOURCES', {})
        if len(dataset_sources) == 0:
            raise click.ClickException(
                'No dataset sources configured. Please add one to the configuration.'
            )
        else:
            print(
                f'Syncing data from ({len(dataset_sources)}) dataset sources')
            print('-' * 80)
            for source_name, source in dataset_sources.items():
                print(f'* Syncing {source_name}...', end="", flush=True)
                start_time = time.time()
                source.sync(db)
                print(
                    f'Finished syncing {source_name} in {time.time() - start_time:.2f} seconds'
                )
