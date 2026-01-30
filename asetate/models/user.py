"""User model - authentication and Discogs credentials storage."""

from datetime import datetime

from flask_login import UserMixin

from asetate import db


class User(UserMixin, db.Model):
    """A user account for storing Discogs credentials.

    Uses Google OAuth for authentication. Discogs OAuth 1.0a tokens
    are stored per-user for syncing their collection.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Google OAuth info
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    picture = db.Column(db.String(500))  # Profile picture URL

    # Discogs OAuth 1.0a credentials (tokens are encrypted)
    discogs_username = db.Column(db.String(100))
    _discogs_token_encrypted = db.Column("discogs_token", db.String(500))
    _discogs_token_secret_encrypted = db.Column("discogs_token_secret", db.String(500))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    releases = db.relationship("Release", back_populates="user", lazy="dynamic")
    crates = db.relationship("Crate", back_populates="user", lazy="dynamic")
    tags = db.relationship("Tag", back_populates="user", lazy="dynamic")
    sync_progress = db.relationship("SyncProgress", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def discogs_token(self) -> str:
        """Decrypt and return the Discogs OAuth token."""
        if not self._discogs_token_encrypted:
            return ""
        from asetate.utils import decrypt_token
        return decrypt_token(self._discogs_token_encrypted)

    @discogs_token.setter
    def discogs_token(self, value: str):
        """Encrypt and store the Discogs OAuth token."""
        if not value:
            self._discogs_token_encrypted = None
        else:
            from asetate.utils import encrypt_token
            self._discogs_token_encrypted = encrypt_token(value)

    @property
    def discogs_token_secret(self) -> str:
        """Decrypt and return the Discogs OAuth token secret."""
        if not self._discogs_token_secret_encrypted:
            return ""
        from asetate.utils import decrypt_token
        return decrypt_token(self._discogs_token_secret_encrypted)

    @discogs_token_secret.setter
    def discogs_token_secret(self, value: str):
        """Encrypt and store the Discogs OAuth token secret."""
        if not value:
            self._discogs_token_secret_encrypted = None
        else:
            from asetate.utils import encrypt_token
            self._discogs_token_secret_encrypted = encrypt_token(value)

    @property
    def has_discogs_credentials(self) -> bool:
        """Check if user has configured Discogs credentials."""
        return bool(
            self.discogs_username
            and self._discogs_token_encrypted
            and self._discogs_token_secret_encrypted
        )

    def update_discogs_credentials(self, username: str, token: str, token_secret: str):
        """Update the user's Discogs OAuth credentials."""
        self.discogs_username = username
        self.discogs_token = token
        self.discogs_token_secret = token_secret

    def clear_discogs_credentials(self):
        """Remove the user's Discogs credentials."""
        self.discogs_username = None
        self._discogs_token_encrypted = None
        self._discogs_token_secret_encrypted = None
