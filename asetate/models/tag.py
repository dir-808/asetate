"""Tag model - labels for categorizing tracks."""

from datetime import datetime

from asetate import db

# Junction table for track-tag relationship
track_tags = db.Table(
    "track_tags",
    db.Column(
        "track_id", db.Integer, db.ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True
    ),
    db.Column(
        "tag_id", db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Tag(db.Model):
    """A tag for categorizing tracks.

    Tags can be used for genres, moods, energy levels, or any other
    categorization the DJ finds useful.
    """

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7))  # Hex color for UI, e.g., "#E07A5F"

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tracks = db.relationship("Track", secondary=track_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"

    @property
    def track_count(self) -> int:
        """Number of tracks with this tag."""
        return len(self.tracks)
