"""User model - authentication and Discogs credentials storage."""

from datetime import datetime

from flask_login import UserMixin

from asetate import db


class User(UserMixin, db.Model):
    """A user account for storing Discogs credentials.

    Uses Google OAuth for authentication. Discogs token and username
    are stored per-user for syncing their collection.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Google OAuth info
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    picture = db.Column(db.String(500))  # Profile picture URL

    # Discogs credentials (stored per user)
    discogs_username = db.Column(db.String(100))
    discogs_token = db.Column(db.String(100))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def has_discogs_credentials(self) -> bool:
        """Check if user has configured Discogs credentials."""
        return bool(self.discogs_username and self.discogs_token)

    def update_discogs_credentials(self, username: str, token: str):
        """Update the user's Discogs credentials."""
        self.discogs_username = username
        self.discogs_token = token
