"""Track model - individual tracks on a release with DJ metadata."""

from datetime import datetime

from asetate import db


class Track(db.Model):
    """An individual track on a vinyl release.

    Contains both Discogs metadata (position, title, duration) and
    user-entered DJ metadata (BPM, key, energy, playable status).
    """

    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(
        db.Integer, db.ForeignKey("releases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Discogs metadata
    position = db.Column(db.String(20))  # A1, A2, B1, etc.
    title = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.String(20))  # "5:32" format from Discogs

    # DJ metadata (user-entered)
    bpm = db.Column(db.Integer, index=True)  # Indexed for range queries
    musical_key = db.Column(db.String(10))  # Standard notation: Am, F#m, Bb, etc.
    camelot = db.Column(db.String(5))  # Camelot wheel: 8A, 11B, etc.
    energy = db.Column(db.Integer)  # 1-10 scale
    is_playable = db.Column(db.Boolean, default=False, nullable=False, index=True)
    notes = db.Column(db.Text)  # Freeform user notes

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    release = db.relationship("Release", back_populates="tracks")
    tags = db.relationship("Tag", secondary="track_tags", back_populates="tracks")

    __table_args__ = (
        db.CheckConstraint("energy >= 1 AND energy <= 10", name="energy_range"),
        db.CheckConstraint("bpm >= 20 AND bpm <= 300", name="bpm_range"),
    )

    def __repr__(self):
        position_str = f"{self.position} - " if self.position else ""
        return f"<Track {position_str}{self.title}>"

    @property
    def display_position(self) -> str:
        """Format position for display, handling missing values."""
        return self.position or "—"

    @property
    def display_duration(self) -> str:
        """Format duration for display, handling missing values."""
        return self.duration or "—"

    @property
    def display_bpm(self) -> str:
        """Format BPM for display, handling missing values."""
        return str(self.bpm) if self.bpm else "—"

    @property
    def display_key(self) -> str:
        """Return Camelot notation if available, otherwise musical key."""
        if self.camelot:
            return self.camelot
        if self.musical_key:
            return self.musical_key
        return "—"
