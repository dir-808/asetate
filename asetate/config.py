"""Application configuration."""

import os
from pathlib import Path


class Config:
    """Base configuration."""

    # Base directory
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Secret key for session management
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'asetate.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Discogs API
    DISCOGS_CONSUMER_KEY = os.environ.get("DISCOGS_CONSUMER_KEY", "")
    DISCOGS_CONSUMER_SECRET = os.environ.get("DISCOGS_CONSUMER_SECRET", "")
    DISCOGS_USER_TOKEN = os.environ.get("DISCOGS_USER_TOKEN", "")

    # Rate limiting for Discogs API (requests per minute)
    DISCOGS_RATE_LIMIT = 60


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
