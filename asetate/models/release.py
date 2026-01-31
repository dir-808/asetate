"""Release model - vinyl records synced from Discogs."""

from datetime import datetime

from asetate import db


class Release(db.Model):
    """A vinyl release from the user's Discogs collection.

    Stores both Discogs metadata and user corrections. The discogs_id
    is used as the unique identifier for syncing to prevent duplicates.
    Each release belongs to a specific user.
    """

    __tablename__ = "releases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    discogs_id = db.Column(db.Integer, nullable=False, index=True)

    # Discogs metadata
    title = db.Column(db.String(500), nullable=False)
    artist = db.Column(db.String(500), nullable=False)
    label = db.Column(db.String(500))
    year = db.Column(db.Integer)
    cover_art_url = db.Column(db.String(1000))
    discogs_uri = db.Column(db.String(500))

    # User corrections (JSON) - local overrides for incorrect Discogs data
    # Format: {"title": "Corrected Title", "artist": "Corrected Artist", ...}
    user_corrections = db.Column(db.JSON)

    # Sync tracking
    synced_at = db.Column(db.DateTime)
    discogs_removed_at = db.Column(db.DateTime)  # Set when removed from Discogs collection
    kept_after_removal = db.Column(db.Boolean)  # User chose to keep locally

    # Inventory data (from Discogs Inventory API - only for items listed for sale)
    listing_id = db.Column(db.Integer, index=True)  # Discogs listing ID
    condition = db.Column(db.String(50))  # e.g., "Mint (M)", "Near Mint (NM or M-)"
    sleeve_condition = db.Column(db.String(50))  # Same scale as condition
    price = db.Column(db.String(50))  # e.g., "£25.00" - stored with currency
    location = db.Column(db.String(200))  # Seller's bin/shelf location
    inventory_synced_at = db.Column(db.DateTime)  # Last inventory sync timestamp

    # Export tracking
    last_exported_at = db.Column(db.DateTime)  # For "export since last export" feature

    # User notes (freeform text for the whole release)
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="releases")
    tracks = db.relationship(
        "Track", back_populates="release", cascade="all, delete-orphan", lazy="dynamic"
    )
    inventory_listings = db.relationship(
        "InventoryListing", back_populates="release", lazy="dynamic"
    )

    # Unique constraint: one discogs_id per user
    __table_args__ = (
        db.UniqueConstraint("user_id", "discogs_id", name="unique_release_per_user"),
    )

    def __repr__(self):
        return f"<Release {self.artist} - {self.title}>"

    @property
    def display_title(self) -> str:
        """Return corrected title if available, otherwise Discogs title."""
        if self.user_corrections and "title" in self.user_corrections:
            return self.user_corrections["title"]
        return self.title

    @property
    def display_artist(self) -> str:
        """Return corrected artist if available, otherwise Discogs artist."""
        if self.user_corrections and "artist" in self.user_corrections:
            return self.user_corrections["artist"]
        return self.artist

    @property
    def is_removed_from_discogs(self) -> bool:
        """Check if this release was removed from the Discogs collection."""
        return self.discogs_removed_at is not None

    @property
    def discogs_edit_url(self) -> str | None:
        """URL to edit this release on Discogs."""
        if self.discogs_id:
            return f"https://www.discogs.com/release/{self.discogs_id}/edit"
        return None

    @property
    def discogs_release_url(self) -> str | None:
        """URL to view this release on Discogs."""
        if self.discogs_id:
            return f"https://www.discogs.com/release/{self.discogs_id}"
        return None

    @property
    def listing_url(self) -> str | None:
        """URL to the Discogs listing (only if listed for sale)."""
        if self.listing_id:
            return f"https://www.discogs.com/sell/item/{self.listing_id}"
        return None

    @property
    def is_for_sale(self) -> bool:
        """Check if this release is currently listed for sale."""
        return self.listing_id is not None

    def clear_inventory_data(self):
        """Clear inventory data (e.g., when item is no longer for sale)."""
        self.listing_id = None
        self.condition = None
        self.sleeve_condition = None
        self.price = None
        self.location = None
        self.inventory_synced_at = None

    def update_inventory_data(
        self,
        listing_id: int,
        condition: str | None = None,
        sleeve_condition: str | None = None,
        price: str | None = None,
        location: str | None = None,
    ):
        """Update inventory data from a Discogs inventory sync."""
        self.listing_id = listing_id
        self.condition = condition
        self.sleeve_condition = sleeve_condition
        self.price = price
        self.location = location
        self.inventory_synced_at = datetime.utcnow()

    def mark_exported(self):
        """Mark release as exported (for tracking export history)."""
        self.last_exported_at = datetime.utcnow()

    @property
    def active_listings_count(self) -> int:
        """Count of active inventory listings for this release."""
        from .inventory_listing import InventoryListing, ListingStatus
        return self.inventory_listings.filter(
            InventoryListing.status.in_([ListingStatus.FOR_SALE, ListingStatus.DRAFT])
        ).count()
