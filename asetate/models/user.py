"""User model - supports both OAuth and Personal Access Token modes."""

from datetime import datetime

from flask_login import UserMixin

from asetate import db


class User(UserMixin, db.Model):
    """A user account for Asetate.

    Supports two authentication modes:
    - OAuth mode (hosted): discogs_id is set, uses oauth_token + oauth_token_secret
    - PAT mode (self-hosted): discogs_id is null, uses personal_access_token
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Discogs identity
    discogs_id = db.Column(db.Integer, unique=True, nullable=True)  # Null in PAT mode
    discogs_username = db.Column(db.String(100), nullable=False)

    # OAuth 1.0a credentials (used in hosted/OAuth mode)
    _oauth_token_encrypted = db.Column("oauth_token", db.String(500))
    _oauth_token_secret_encrypted = db.Column("oauth_token_secret", db.String(500))

    # Personal Access Token (used in self-hosted/PAT mode)
    _personal_token_encrypted = db.Column("personal_token", db.String(500))

    # User preferences (stored as JSON)
    # Example: {"seller_mode": true, "include_inventory_url": true}
    preferences = db.Column(db.JSON, nullable=False, default=dict)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    releases = db.relationship("Release", back_populates="user", lazy="dynamic")
    crates = db.relationship("Crate", back_populates="user", lazy="dynamic")
    tags = db.relationship("Tag", back_populates="user", lazy="dynamic")
    sync_progress = db.relationship("SyncProgress", back_populates="user", lazy="dynamic")
    inventory_listings = db.relationship("InventoryListing", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.discogs_username}>"

    # =========================================================================
    # OAuth token properties (for hosted mode)
    # =========================================================================

    @property
    def oauth_token(self) -> str:
        """Decrypt and return the OAuth token."""
        if not self._oauth_token_encrypted:
            return ""
        from asetate.utils import decrypt_token
        return decrypt_token(self._oauth_token_encrypted)

    @oauth_token.setter
    def oauth_token(self, value: str):
        """Encrypt and store the OAuth token."""
        if not value:
            self._oauth_token_encrypted = None
        else:
            from asetate.utils import encrypt_token
            self._oauth_token_encrypted = encrypt_token(value)

    @property
    def oauth_token_secret(self) -> str:
        """Decrypt and return the OAuth token secret."""
        if not self._oauth_token_secret_encrypted:
            return ""
        from asetate.utils import decrypt_token
        return decrypt_token(self._oauth_token_secret_encrypted)

    @oauth_token_secret.setter
    def oauth_token_secret(self, value: str):
        """Encrypt and store the OAuth token secret."""
        if not value:
            self._oauth_token_secret_encrypted = None
        else:
            from asetate.utils import encrypt_token
            self._oauth_token_secret_encrypted = encrypt_token(value)

    # =========================================================================
    # Personal Access Token properties (for self-hosted mode)
    # =========================================================================

    @property
    def personal_token(self) -> str:
        """Decrypt and return the Personal Access Token."""
        if not self._personal_token_encrypted:
            return ""
        from asetate.utils import decrypt_token
        return decrypt_token(self._personal_token_encrypted)

    @personal_token.setter
    def personal_token(self, value: str):
        """Encrypt and store the Personal Access Token."""
        if not value:
            self._personal_token_encrypted = None
        else:
            from asetate.utils import encrypt_token
            self._personal_token_encrypted = encrypt_token(value)

    # =========================================================================
    # Credential helpers
    # =========================================================================

    @property
    def has_discogs_credentials(self) -> bool:
        """Check if user has valid Discogs credentials (either mode)."""
        has_oauth = bool(self._oauth_token_encrypted and self._oauth_token_secret_encrypted)
        has_pat = bool(self._personal_token_encrypted)
        return has_oauth or has_pat

    @property
    def is_oauth_user(self) -> bool:
        """Check if this user authenticated via OAuth."""
        return self.discogs_id is not None

    def update_oauth_tokens(self, token: str, token_secret: str):
        """Update the user's OAuth tokens."""
        self.oauth_token = token
        self.oauth_token_secret = token_secret
        # Clear PAT if switching to OAuth
        self._personal_token_encrypted = None

    def update_personal_token(self, username: str, token: str):
        """Update the user's Personal Access Token."""
        self.discogs_username = username
        self.personal_token = token
        # Clear OAuth tokens if switching to PAT
        self._oauth_token_encrypted = None
        self._oauth_token_secret_encrypted = None

    # Legacy property aliases for backward compatibility with sync service
    @property
    def discogs_token(self) -> str:
        """Get the appropriate token for API calls."""
        if self._personal_token_encrypted:
            return self.personal_token
        return self.oauth_token

    @property
    def discogs_token_secret(self) -> str:
        """Get the OAuth token secret (empty for PAT mode)."""
        return self.oauth_token_secret

    # =========================================================================
    # Seller settings helpers
    # =========================================================================

    @property
    def is_seller_mode(self) -> bool:
        """Check if seller mode is enabled."""
        prefs = self.preferences or {}
        return prefs.get("seller_mode", False)

    @property
    def include_inventory_url(self) -> bool:
        """Check if inventory URL should be included in exports."""
        prefs = self.preferences or {}
        return prefs.get("include_inventory_url", False)

    @property
    def include_drafts(self) -> bool:
        """Check if draft listings should be included in inventory sync."""
        prefs = self.preferences or {}
        return prefs.get("include_drafts", False)

    def update_seller_settings(
        self,
        seller_mode: bool = None,
        include_inventory_url: bool = None,
        include_drafts: bool = None,
    ):
        """Update seller-related preferences."""
        prefs = dict(self.preferences or {})
        if seller_mode is not None:
            prefs["seller_mode"] = seller_mode
        if include_inventory_url is not None:
            prefs["include_inventory_url"] = include_inventory_url
        if include_drafts is not None:
            prefs["include_drafts"] = include_drafts
        self.preferences = prefs

    # =========================================================================
    # Field visibility settings
    # =========================================================================

    # Default visible fields for tracks table
    DEFAULT_TRACK_FIELDS = ["position", "title", "duration", "bpm", "key", "energy", "tags", "playable"]

    @property
    def visible_track_fields(self) -> list[str]:
        """Get list of visible fields for tracks table."""
        prefs = self.preferences or {}
        return prefs.get("visible_track_fields", self.DEFAULT_TRACK_FIELDS)

    def set_visible_track_fields(self, fields: list[str]):
        """Set which fields are visible in the tracks table."""
        prefs = dict(self.preferences or {})
        prefs["visible_track_fields"] = fields
        self.preferences = prefs
