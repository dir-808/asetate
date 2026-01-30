"""Command-line interface for Asetate."""

import click
from flask.cli import FlaskGroup

from asetate import create_app


def create_cli_app():
    """Create the app for CLI context."""
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def main():
    """Asetate - DJ library manager for vinyl collectors."""
    pass


if __name__ == "__main__":
    main()
