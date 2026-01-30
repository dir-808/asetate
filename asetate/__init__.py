"""Asetate - A local-first DJ library manager for vinyl collectors."""

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import config

__version__ = "0.1.0"

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


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
    limiter.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Context processor to expose mode info to templates
    @app.context_processor
    def inject_app_mode():
        """Make OAuth mode flag available to all templates."""
        consumer_key = app.config.get("DISCOGS_CONSUMER_KEY")
        consumer_secret = app.config.get("DISCOGS_CONSUMER_SECRET")
        return {"oauth_mode": bool(consumer_key and consumer_secret)}

    # Register blueprints
    from .routes import main, releases, crates, sync, export, tags, auth

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(releases.bp, url_prefix="/releases")
    app.register_blueprint(crates.bp, url_prefix="/crates")
    app.register_blueprint(sync.bp, url_prefix="/sync")
    app.register_blueprint(export.bp, url_prefix="/export")
    app.register_blueprint(tags.bp, url_prefix="/tags")

    return app
