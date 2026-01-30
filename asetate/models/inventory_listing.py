"""InventoryListing model - items listed for sale on Discogs."""

from datetime import datetime

from asetate import db


class ListingStatus:
    """Status constants for inventory listings."""

    FOR_SALE = "for_sale"
    DRAFT = "draft"
    SOLD = "sold"
    REMOVED = "removed"


class InventoryListing(db.Model):
    """An inventory listing from Discogs (items for sale).

    Supports multiple listings per release (e.g., multiple copies at different
    conditions/prices) and listings not in collection (consignment/flip items).
    """

    __tablename__ = "inventory_listings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Link to local release (nullable - listing may not be in collection)
    release_id = db.Column(
        db.Integer, db.ForeignKey("releases.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Discogs identifiers
    listing_id = db.Column(db.Integer, nullable=False, index=True)
    discogs_release_id = db.Column(db.Integer, nullable=False, index=True)

    # Release info (cached from Discogs for listings not in collection)
    release_title = db.Column(db.String(500))
    release_artist = db.Column(db.String(500))

    # Listing details
    condition = db.Column(db.String(50))  # e.g., "Mint (M)", "Near Mint (NM or M-)"
    sleeve_condition = db.Column(db.String(50))
    price = db.Column(db.String(50))  # e.g., "£25.00"
    original_price = db.Column(db.String(50))  # Price with original currency
    location = db.Column(db.String(200))  # Seller's bin/shelf location
    comments = db.Column(db.Text)  # Listing comments/notes

    # Status tracking
    status = db.Column(db.String(20), nullable=False, default=ListingStatus.FOR_SALE)
    listed_at = db.Column(db.DateTime)  # When originally listed
    sold_at = db.Column(db.DateTime)  # When sold (status changed to sold)
    removed_at = db.Column(db.DateTime)  # When removed from inventory

    # Sync and export tracking
    synced_at = db.Column(db.DateTime)
    last_exported_at = db.Column(db.DateTime)  # For "export since last export" feature

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Notification tracking
    notification_dismissed = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship("User", back_populates="inventory_listings")
    release = db.relationship("Release", back_populates="inventory_listings")

    # Unique constraint: one listing_id per user
    __table_args__ = (
        db.UniqueConstraint("user_id", "listing_id", name="unique_listing_per_user"),
    )

    def __repr__(self):
        return f"<InventoryListing {self.listing_id}: {self.release_artist} - {self.release_title}>"

    @property
    def listing_url(self) -> str:
        """URL to the Discogs listing."""
        return f"https://www.discogs.com/sell/item/{self.listing_id}"

    @property
    def discogs_release_url(self) -> str:
        """URL to the Discogs release page."""
        return f"https://www.discogs.com/release/{self.discogs_release_id}"

    @property
    def is_active(self) -> bool:
        """Check if listing is currently active (for sale or draft)."""
        return self.status in (ListingStatus.FOR_SALE, ListingStatus.DRAFT)

    @property
    def is_sold(self) -> bool:
        """Check if listing was sold."""
        return self.status == ListingStatus.SOLD

    @property
    def is_in_collection(self) -> bool:
        """Check if this listing has a matching release in collection."""
        return self.release_id is not None

    @property
    def display_title(self) -> str:
        """Get display title (from release if linked, otherwise cached)."""
        if self.release:
            return self.release.display_title
        return self.release_title or "Unknown"

    @property
    def display_artist(self) -> str:
        """Get display artist (from release if linked, otherwise cached)."""
        if self.release:
            return self.release.display_artist
        return self.release_artist or "Unknown"

    @property
    def needs_attention(self) -> bool:
        """Check if this listing needs user attention (sold/removed, not dismissed)."""
        return (
            self.status in (ListingStatus.SOLD, ListingStatus.REMOVED)
            and not self.notification_dismissed
        )

    def mark_sold(self):
        """Mark listing as sold."""
        self.status = ListingStatus.SOLD
        self.sold_at = datetime.utcnow()
        self.notification_dismissed = False

    def mark_removed(self):
        """Mark listing as removed from inventory."""
        self.status = ListingStatus.REMOVED
        self.removed_at = datetime.utcnow()
        self.notification_dismissed = False

    def dismiss_notification(self):
        """Dismiss the sold/removed notification."""
        self.notification_dismissed = True

    def update_from_discogs(
        self,
        condition: str | None = None,
        sleeve_condition: str | None = None,
        price: str | None = None,
        location: str | None = None,
        comments: str | None = None,
        status: str | None = None,
        release_title: str | None = None,
        release_artist: str | None = None,
    ):
        """Update listing data from a Discogs sync."""
        if condition is not None:
            self.condition = condition
        if sleeve_condition is not None:
            self.sleeve_condition = sleeve_condition
        if price is not None:
            self.price = price
            self.original_price = price
        if location is not None:
            self.location = location
        if comments is not None:
            self.comments = comments
        if status is not None:
            self.status = status
        if release_title is not None:
            self.release_title = release_title
        if release_artist is not None:
            self.release_artist = release_artist
        self.synced_at = datetime.utcnow()

    def mark_exported(self):
        """Mark listing as exported (for tracking export history)."""
        self.last_exported_at = datetime.utcnow()
