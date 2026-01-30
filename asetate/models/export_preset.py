"""Export preset model - saved configurations for CSV exports."""

from datetime import datetime

from asetate import db


class ExportPreset(db.Model):
    """A saved export configuration for generating filtered CSVs.

    Stores filter criteria and column selection for repeatable exports,
    e.g., "All playable House tracks 120-130 BPM for label printing."
    Each preset belongs to a specific user.
    """

    __tablename__ = "export_presets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = db.Column(db.String(200), nullable=False)

    # Relationships
    user = db.relationship("User", backref=db.backref("export_presets", lazy="dynamic"))

    # Filter configuration (stored as JSON)
    # Example: {
    #   "crate_ids": [1, 2],
    #   "bpm_min": 120,
    #   "bpm_max": 130,
    #   "is_playable": true,
    #   "tags": ["house", "deep"],
    #   "energy_min": 5
    # }
    filters = db.Column(db.JSON, nullable=False, default=dict)

    # Column selection (stored as JSON array)
    # Example: ["artist", "title", "bpm", "key", "position"]
    columns = db.Column(db.JSON, nullable=False, default=list)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Unique constraint: preset names unique per user
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="unique_preset_name_per_user"),
    )

    def __repr__(self):
        return f"<ExportPreset {self.name}>"

    # Available columns for export
    AVAILABLE_COLUMNS = [
        ("artist", "Artist"),
        ("release_title", "Release"),
        ("track_title", "Track Title"),
        ("position", "Side/Track"),
        ("label", "Label"),
        ("year", "Year"),
        ("bpm", "BPM"),
        ("musical_key", "Key"),
        ("camelot", "Camelot"),
        ("energy", "Energy"),
        ("duration", "Duration"),
        ("notes", "Notes"),
        ("tags", "Tags"),
        ("crates", "Crates"),
        ("release_url", "Discogs URL"),
        ("discogs_id", "Discogs ID"),
    ]

    # Seller-only columns (shown when seller mode enabled)
    SELLER_COLUMNS = [
        ("release_url", "Discogs URL"),
        ("discogs_id", "Discogs ID"),
    ]

    @classmethod
    def get_default_columns(cls) -> list[str]:
        """Return default columns for a new export."""
        return ["artist", "release_title", "track_title", "position", "bpm", "musical_key"]
