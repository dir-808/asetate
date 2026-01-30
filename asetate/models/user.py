"""User model - Discogs OAuth authentication."""

from datetime import datetime

from flask_login import UserMixin

from asetate import db


class User(UserMixin, db.Model):
    """A user account authenticated via Discogs OAuth.

    Uses Discogs OAuth 1.0a for authentication. The discogs_id serves
    as the unique identifier for each user.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Discogs identity (from OAuth)
    discogs_id = db.Column(db.Integer, unique=True, nullable=False)
    discogs_username = db.Column(db.String(100), nullable=False)

    # Discogs OAuth 1.0a credentials (tokens are encrypted)
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
        return f"<User {self.discogs_username}>"

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
        """Check if user has valid Discogs credentials."""
        return bool(
            self._discogs_token_encrypted
            and self._discogs_token_secret_encrypted
        )

    def update_tokens(self, token: str, token_secret: str):
        """Update the user's Discogs OAuth tokens."""
        self.discogs_token = token
        self.discogs_token_secret = token_secret
