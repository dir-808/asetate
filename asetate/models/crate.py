"""Crate model - organizational containers for releases and tracks."""

from datetime import datetime

from asetate import db

# Preset colors for crates (Notion-inspired palette)
CRATE_COLORS = [
    {"id": "gray", "hex": "#787774", "name": "Gray"},
    {"id": "brown", "hex": "#9F6B53", "name": "Brown"},
    {"id": "orange", "hex": "#D9730D", "name": "Orange"},
    {"id": "yellow", "hex": "#CB912F", "name": "Yellow"},
    {"id": "green", "hex": "#448361", "name": "Green"},
    {"id": "blue", "hex": "#337EA9", "name": "Blue"},
    {"id": "purple", "hex": "#9065B0", "name": "Purple"},
    {"id": "pink", "hex": "#C14C8A", "name": "Pink"},
    {"id": "red", "hex": "#D44C47", "name": "Red"},
]

# Preset icons for crates (emoji-based, music/DJ themed)
CRATE_ICONS = [
    # Music & Audio
    "🎵", "🎶", "🎧", "🎤", "🎹", "🎸", "🎺", "🎷", "🥁", "🪘",
    # Vinyl & DJ
    "💿", "📀", "🎚️", "🎛️",
    # Genres/Moods
    "🔥", "❄️", "🌙", "☀️", "⭐", "💫", "✨", "🌈", "🌊", "🌴",
    # Categories
    "📁", "📂", "🗂️", "📦", "🏷️", "🔖",
    # Energy/Vibe
    "💃", "🕺", "🪩", "🎉", "🎊", "💎", "👑", "🏆",
    # Colors/Abstract
    "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "⚫", "⚪", "🟤",
    # Other
    "❤️", "💜", "💙", "💚", "💛", "🧡", "🖤", "🤍",
]

# Junction table for crates containing releases
crate_releases = db.Table(
    "crate_releases",
    db.Column(
        "crate_id", db.Integer, db.ForeignKey("crates.id", ondelete="CASCADE"), primary_key=True
    ),
    db.Column(
        "release_id",
        db.Integer,
        db.ForeignKey("releases.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("added_at", db.DateTime, default=datetime.utcnow),
)

# Junction table for crates containing individual tracks
crate_tracks = db.Table(
    "crate_tracks",
    db.Column(
        "crate_id", db.Integer, db.ForeignKey("crates.id", ondelete="CASCADE"), primary_key=True
    ),
    db.Column(
        "track_id", db.Integer, db.ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True
    ),
    db.Column("added_at", db.DateTime, default=datetime.utcnow),
)


class Crate(db.Model):
    """A crate for organizing releases and/or individual tracks.

    Supports hierarchical organization through self-referential parent_id.
    Crates can contain whole releases and/or cherry-picked individual tracks.
    Each crate belongs to a specific user.
    """

    __tablename__ = "crates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id = db.Column(
        db.Integer, db.ForeignKey("crates.id", ondelete="CASCADE"), index=True
    )  # NULL = top-level crate
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20))  # Preset color ID or hex color
    icon = db.Column(db.String(10))   # Emoji icon
    sort_order = db.Column(db.Integer, default=0)  # For manual ordering

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="crates")

    # Self-referential relationship for hierarchy
    children = db.relationship(
        "Crate",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # Many-to-many relationships
    releases = db.relationship(
        "Release", secondary=crate_releases, backref=db.backref("crates", lazy="dynamic")
    )
    tracks = db.relationship(
        "Track", secondary=crate_tracks, backref=db.backref("crates", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "parent_id", "name", name="unique_name_per_user_parent"),
    )

    def __repr__(self):
        return f"<Crate {self.name}>"

    @property
    def color_hex(self) -> str | None:
        """Get the hex color value for this crate."""
        if not self.color:
            return None
        # Check if it's a preset color ID
        for preset in CRATE_COLORS:
            if preset["id"] == self.color:
                return preset["hex"]
        # Otherwise assume it's already a hex color
        if self.color.startswith("#"):
            return self.color
        return None

    @property
    def display_icon(self) -> str:
        """Get the icon to display, with fallback to folder emoji."""
        return self.icon or "📁"

    @property
    def is_top_level(self) -> bool:
        """Check if this is a top-level crate (no parent)."""
        return self.parent_id is None

    @property
    def full_path(self) -> str:
        """Return the full path of this crate (e.g., 'House / Deep House / Classics')."""
        if self.parent:
            return f"{self.parent.full_path} / {self.name}"
        return self.name

    @property
    def depth(self) -> int:
        """Return the nesting depth (0 for top-level)."""
        if self.parent:
            return self.parent.depth + 1
        return 0

    def get_all_tracks(self):
        """Get all tracks in this crate.

        Returns both directly added tracks and all tracks from releases in this crate.
        """
        from .track import Track
        from .release import Release

        # Tracks directly in this crate
        direct_tracks = set(self.tracks)

        # Tracks from releases in this crate
        for release in self.releases:
            direct_tracks.update(release.tracks)

        return list(direct_tracks)

    def get_all_playable_tracks(self):
        """Get all playable tracks in this crate."""
        return [t for t in self.get_all_tracks() if t.is_playable]
