"""Asetate - A local-first DJ library manager for vinyl collectors."""

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import config

__version__ = "0.1.0"

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = "default") -> Flask:
    """Application factory for creating the Flask app.

    Args:
        config_name: Configuration to use (development, production, testing)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes import main, releases, crates, sync, export

    app.register_blueprint(main.bp)
    app.register_blueprint(releases.bp, url_prefix="/releases")
    app.register_blueprint(crates.bp, url_prefix="/crates")
    app.register_blueprint(sync.bp, url_prefix="/sync")
    app.register_blueprint(export.bp, url_prefix="/export")

    return app
