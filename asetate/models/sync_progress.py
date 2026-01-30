"""Sync progress model - tracks Discogs collection sync status."""

from datetime import datetime
from enum import Enum

from asetate import db


class SyncStatus(str, Enum):
    """Status of a sync operation."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncProgress(db.Model):
    """Tracks the progress of a Discogs collection sync.

    Allows for resumable syncs when dealing with large collections
    and Discogs API rate limits (60 requests/minute).
    Each sync belongs to a specific user.
    """

    __tablename__ = "sync_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Progress tracking
    status = db.Column(db.String(20), default=SyncStatus.PENDING.value, nullable=False)
    total_releases = db.Column(db.Integer, default=0)
    processed_releases = db.Column(db.Integer, default=0)
    added_releases = db.Column(db.Integer, default=0)
    updated_releases = db.Column(db.Integer, default=0)
    removed_releases = db.Column(db.Integer, default=0)

    # Pagination tracking (for resuming)
    current_page = db.Column(db.Integer, default=1)
    per_page = db.Column(db.Integer, default=100)

    # Error handling
    last_error = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)

    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="sync_progress")

    def __repr__(self):
        return f"<SyncProgress {self.status} {self.processed_releases}/{self.total_releases}>"

    @property
    def progress_percent(self) -> float:
        """Calculate sync progress as a percentage."""
        if self.total_releases == 0:
            return 0.0
        return (self.processed_releases / self.total_releases) * 100

    @property
    def is_complete(self) -> bool:
        """Check if sync is complete."""
        return self.status == SyncStatus.COMPLETED.value

    @property
    def is_running(self) -> bool:
        """Check if sync is currently running."""
        return self.status == SyncStatus.RUNNING.value

    @property
    def can_resume(self) -> bool:
        """Check if this sync can be resumed."""
        return self.status in (SyncStatus.PAUSED.value, SyncStatus.FAILED.value)

    def start(self):
        """Mark sync as started."""
        self.status = SyncStatus.RUNNING.value
        self.started_at = datetime.utcnow()

    def pause(self):
        """Pause the sync (can be resumed later)."""
        self.status = SyncStatus.PAUSED.value

    def complete(self):
        """Mark sync as complete."""
        self.status = SyncStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()

    def fail(self, error: str):
        """Mark sync as failed with error message."""
        self.status = SyncStatus.FAILED.value
        self.last_error = error
        self.retry_count += 1

    @classmethod
    def get_latest(cls, user_id: int | None = None) -> "SyncProgress | None":
        """Get the most recent sync progress record for a user."""
        query = cls.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.order_by(cls.created_at.desc()).first()

    @classmethod
    def get_or_create_active(cls, user_id: int) -> "SyncProgress":
        """Get an active (resumable) sync or create a new one for a user."""
        active = cls.query.filter(
            cls.user_id == user_id,
            cls.status.in_([SyncStatus.RUNNING.value, SyncStatus.PAUSED.value])
        ).first()
        if active:
            return active

        new_sync = cls(user_id=user_id)
        db.session.add(new_sync)
        return new_sync
