"""Collection sync service - orchestrates Discogs to local database sync."""

from datetime import datetime
from typing import Callable

from asetate import db
from asetate.models import Release, Track, SyncProgress
from asetate.models.sync_progress import SyncStatus
from asetate.services.discogs import (
    DiscogsClient,
    DiscogsRelease,
    DiscogsRateLimitError,
    InventoryItem,
)

import time


class SyncService:
    """Service for syncing Discogs collection to local database.

    Handles:
    - Fetching collection with rate limiting
    - Upserting releases and tracks (no duplicates)
    - Detecting removed releases
    - Progress tracking and resume capability

    Supports both OAuth and Personal Access Token authentication modes.
    """

    def __init__(
        self,
        user_id: int,
        discogs_username: str,
        oauth_token: str | None = None,
        oauth_token_secret: str | None = None,
        personal_token: str | None = None,
        progress_callback: Callable[[SyncProgress], None] | None = None,
    ):
        """Initialize the sync service.

        Args:
            user_id: The user ID to sync for (required for user isolation).
            discogs_username: Discogs username (required).
            oauth_token: Discogs OAuth access token (for OAuth mode).
            oauth_token_secret: Discogs OAuth access token secret (for OAuth mode).
            personal_token: Discogs Personal Access Token (for PAT mode).
            progress_callback: Optional callback called after each release is processed.
                              Receives the current SyncProgress object.
        """
        self.user_id = user_id
        self.discogs_username = discogs_username
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.personal_token = personal_token
        self.progress_callback = progress_callback
        self.client: DiscogsClient | None = None

    @classmethod
    def from_user(cls, user, progress_callback=None) -> "SyncService":
        """Create a SyncService from a User object.

        Automatically detects whether to use OAuth or PAT based on user's credentials.

        Args:
            user: User model instance
            progress_callback: Optional callback for progress updates

        Returns:
            Configured SyncService
        """
        if user._personal_token_encrypted:
            return cls(
                user_id=user.id,
                discogs_username=user.discogs_username,
                personal_token=user.personal_token,
                progress_callback=progress_callback,
            )
        else:
            return cls(
                user_id=user.id,
                discogs_username=user.discogs_username,
                oauth_token=user.oauth_token,
                oauth_token_secret=user.oauth_token_secret,
                progress_callback=progress_callback,
            )

    def start_sync(self, resume: bool = False) -> SyncProgress:
        """Start or resume a collection sync.

        Args:
            resume: If True, resume an existing paused/failed sync

        Returns:
            SyncProgress object tracking this sync
        """
        # Create client based on available credentials
        if self.personal_token:
            self.client = DiscogsClient(personal_token=self.personal_token)
        else:
            self.client = DiscogsClient(
                oauth_token=self.oauth_token,
                oauth_token_secret=self.oauth_token_secret,
            )
        username = self.discogs_username

        # Get or create sync progress for this user
        if resume:
            progress = SyncProgress.get_or_create_active(self.user_id)
            if progress.is_complete:
                # Start fresh if last sync was complete
                progress = SyncProgress(user_id=self.user_id)
                db.session.add(progress)
        else:
            progress = SyncProgress(user_id=self.user_id)
            db.session.add(progress)

        progress.start()
        db.session.commit()

        try:
            self._run_sync(username, progress)
        except DiscogsRateLimitError as e:
            # Pause sync, can be resumed later
            progress.pause()
            progress.last_error = f"Rate limited. Retry after {e.retry_after}s"
            db.session.commit()
            raise
        except Exception as e:
            progress.fail(str(e))
            db.session.commit()
            raise

        return progress

    def _run_sync(self, username: str, progress: SyncProgress):
        """Execute the sync process.

        Args:
            username: Discogs username
            progress: SyncProgress to update
        """
        # Track which discogs_ids we see (for detecting removals)
        seen_discogs_ids = set()

        # Iterate through collection
        for item, processed, total in self.client.iter_collection(
            username, start_page=progress.current_page
        ):
            # Update total on first item
            if progress.total_releases == 0:
                progress.total_releases = total

            # Get full release details (includes tracklist)
            basic_info = item.get("basic_information", {})
            discogs_id = basic_info.get("id")

            if not discogs_id:
                continue

            seen_discogs_ids.add(discogs_id)

            try:
                details = self.client.get_release_details(discogs_id)
                release_data = self.client.parse_release(item, details)
                was_new = self._upsert_release(release_data)

                if was_new:
                    progress.added_releases += 1
                else:
                    progress.updated_releases += 1

            except DiscogsRateLimitError:
                # Save progress before re-raising
                progress.current_page = (processed // 100) + 1
                db.session.commit()
                raise
            except Exception as e:
                # Log error but continue with next release
                progress.last_error = f"Error on release {discogs_id}: {str(e)}"

            progress.processed_releases = processed
            db.session.commit()

            # Call progress callback if provided
            if self.progress_callback:
                self.progress_callback(progress)

        # Detect removed releases for this user
        self._mark_removed_releases(seen_discogs_ids, progress)

        progress.complete()
        db.session.commit()

    def _upsert_release(self, release_data: DiscogsRelease) -> bool:
        """Insert or update a release and its tracks.

        Args:
            release_data: Parsed release from Discogs

        Returns:
            True if this was a new release, False if updated
        """
        # Check if release exists for this user
        release = Release.query.filter_by(
            user_id=self.user_id,
            discogs_id=release_data.discogs_id
        ).first()
        is_new = release is None

        if is_new:
            release = Release(
                user_id=self.user_id,
                discogs_id=release_data.discogs_id
            )
            db.session.add(release)

        # Update Discogs fields (always overwrite with fresh data)
        release.title = release_data.title
        release.artist = release_data.artist
        release.label = release_data.label
        release.year = release_data.year
        release.cover_art_url = release_data.cover_art_url
        release.discogs_uri = release_data.discogs_uri
        release.synced_at = datetime.utcnow()

        # Clear removed status if it was previously removed
        if release.discogs_removed_at:
            release.discogs_removed_at = None
            release.kept_after_removal = None

        db.session.flush()  # Get release.id for tracks

        # Sync tracks
        self._sync_tracks(release, release_data.tracks)

        return is_new

    def _sync_tracks(self, release: Release, track_data: list[dict]):
        """Sync tracks for a release.

        Preserves user-entered DJ metadata (BPM, key, etc.) while updating
        Discogs metadata (position, title, duration).

        Args:
            release: The Release object
            track_data: List of track dicts from Discogs
        """
        # Index existing tracks by position for matching
        existing_tracks = {t.position: t for t in release.tracks if t.position}

        # Track which positions we've seen
        seen_positions = set()

        for td in track_data:
            position = td.get("position", "")
            seen_positions.add(position)

            if position in existing_tracks:
                # Update existing track (preserve DJ metadata)
                track = existing_tracks[position]
                track.title = td.get("title", track.title)
                track.duration = td.get("duration") or track.duration
            else:
                # Create new track
                track = Track(
                    release_id=release.id,
                    position=position,
                    title=td.get("title", "Untitled"),
                    duration=td.get("duration"),
                )
                db.session.add(track)

        # Remove tracks that no longer exist on Discogs
        # (only if they have no user data)
        for position, track in existing_tracks.items():
            if position not in seen_positions:
                # Only delete if no user data was added
                if not self._track_has_user_data(track):
                    db.session.delete(track)

    def _track_has_user_data(self, track: Track) -> bool:
        """Check if a track has any user-entered data."""
        return any(
            [
                track.bpm is not None,
                track.musical_key is not None,
                track.camelot is not None,
                track.energy is not None,
                track.is_playable,
                track.notes,
                len(track.tags) > 0,
            ]
        )

    def _mark_removed_releases(self, seen_ids: set[int], progress: SyncProgress):
        """Mark releases that are no longer in the Discogs collection.

        Args:
            seen_ids: Set of discogs_ids seen during this sync
            progress: SyncProgress to update
        """
        # Find releases for this user that weren't seen in this sync
        # (and aren't already marked as removed)
        removed_releases = Release.query.filter(
            Release.user_id == self.user_id,
            Release.discogs_id.notin_(seen_ids),
            Release.discogs_removed_at.is_(None),
        ).all()

        for release in removed_releases:
            release.discogs_removed_at = datetime.utcnow()
            progress.removed_releases += 1


def get_sync_status(user_id: int) -> dict:
    """Get current sync status for the UI.

    Args:
        user_id: The user to get sync status for

    Returns:
        Dict with sync status info
    """
    latest = SyncProgress.get_latest(user_id=user_id)

    if not latest:
        return {
            "status": "never_synced",
            "message": "Collection not synced yet",
            "can_sync": True,
            "can_resume": False,
        }

    return {
        "status": latest.status,
        "progress_percent": round(latest.progress_percent, 1),
        "processed": latest.processed_releases,
        "total": latest.total_releases,
        "added": latest.added_releases,
        "updated": latest.updated_releases,
        "removed": latest.removed_releases,
        "started_at": latest.started_at.isoformat() if latest.started_at else None,
        "completed_at": latest.completed_at.isoformat() if latest.completed_at else None,
        "last_error": latest.last_error,
        "can_sync": not latest.is_running,
        "can_resume": latest.can_resume,
        "message": _get_status_message(latest),
    }


def _get_status_message(progress: SyncProgress) -> str:
    """Generate a human-readable status message."""
    if progress.status == SyncStatus.RUNNING.value:
        return f"Syncing... {progress.processed_releases} of {progress.total_releases} releases"
    elif progress.status == SyncStatus.PAUSED.value:
        return "Sync paused - can be resumed"
    elif progress.status == SyncStatus.COMPLETED.value:
        return f"Last sync completed. {progress.added_releases} new, {progress.updated_releases} updated."
    elif progress.status == SyncStatus.FAILED.value:
        return f"Sync failed: {progress.last_error}"
    else:
        return "Ready to sync"


# =============================================================================
# Inventory Sync Service
# =============================================================================


class InventorySyncService:
    """Service for syncing Discogs inventory data to local releases.

    Updates existing releases with inventory information:
    - listing_id, condition, sleeve_condition, price, location

    This is separate from collection sync - inventory only covers items for sale.
    """

    def __init__(
        self,
        user_id: int,
        discogs_username: str,
        oauth_token: str | None = None,
        oauth_token_secret: str | None = None,
        personal_token: str | None = None,
    ):
        """Initialize the inventory sync service.

        Args:
            user_id: The user ID to sync for.
            discogs_username: Discogs username.
            oauth_token: Discogs OAuth access token (for OAuth mode).
            oauth_token_secret: Discogs OAuth access token secret (for OAuth mode).
            personal_token: Discogs Personal Access Token (for PAT mode).
        """
        self.user_id = user_id
        self.discogs_username = discogs_username
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.personal_token = personal_token
        self.client: DiscogsClient | None = None

    @classmethod
    def from_user(cls, user) -> "InventorySyncService":
        """Create an InventorySyncService from a User object.

        Args:
            user: User model instance

        Returns:
            Configured InventorySyncService
        """
        if user._personal_token_encrypted:
            return cls(
                user_id=user.id,
                discogs_username=user.discogs_username,
                personal_token=user.personal_token,
            )
        else:
            return cls(
                user_id=user.id,
                discogs_username=user.discogs_username,
                oauth_token=user.oauth_token,
                oauth_token_secret=user.oauth_token_secret,
            )

    def _get_client(self) -> DiscogsClient:
        """Get or create the Discogs client."""
        if self.client is None:
            if self.personal_token:
                self.client = DiscogsClient(personal_token=self.personal_token)
            else:
                self.client = DiscogsClient(
                    oauth_token=self.oauth_token,
                    oauth_token_secret=self.oauth_token_secret,
                )
        return self.client

    def sync_full_inventory(self) -> dict:
        """Sync all inventory data to matching releases.

        Returns:
            Stats dict with counts: matched, not_found, cleared
        """
        client = self._get_client()

        stats = {
            "matched": 0,      # Releases updated with inventory data
            "not_found": 0,    # Inventory items without matching release in collection
            "cleared": 0,      # Releases no longer in inventory (data cleared)
            "total_listings": 0,
        }

        # Track which release IDs we see in inventory
        seen_release_ids = set()

        # Iterate through all inventory listings
        for listing, processed, total in client.iter_inventory(self.discogs_username):
            stats["total_listings"] = total

            release_id = listing.get("release", {}).get("id")
            if not release_id:
                continue

            seen_release_ids.add(release_id)
            inventory_item = client.parse_inventory_item(listing)

            # Find matching release in user's collection
            release = Release.query.filter_by(
                user_id=self.user_id,
                discogs_id=release_id,
            ).first()

            if release:
                release.update_inventory_data(
                    listing_id=inventory_item.listing_id,
                    condition=inventory_item.condition,
                    sleeve_condition=inventory_item.sleeve_condition,
                    price=inventory_item.price,
                    location=inventory_item.location,
                )
                stats["matched"] += 1
            else:
                stats["not_found"] += 1

        # Clear inventory data for releases no longer in inventory
        releases_with_inventory = Release.query.filter(
            Release.user_id == self.user_id,
            Release.listing_id.isnot(None),
            Release.discogs_id.notin_(seen_release_ids) if seen_release_ids else True,
        ).all()

        for release in releases_with_inventory:
            release.clear_inventory_data()
            stats["cleared"] += 1

        db.session.commit()
        return stats

    def sync_single_release(self, release_id: int) -> dict:
        """Sync inventory data for a single release.

        Args:
            release_id: The local Release.id (not discogs_id)

        Returns:
            Status dict with result info
        """
        client = self._get_client()

        # Find the release
        release = Release.query.filter_by(
            id=release_id,
            user_id=self.user_id,
        ).first()

        if not release:
            return {"success": False, "error": "Release not found"}

        # Search inventory for this release
        inventory_item = client.get_inventory_for_release(
            self.discogs_username,
            release.discogs_id,
        )

        if inventory_item:
            release.update_inventory_data(
                listing_id=inventory_item.listing_id,
                condition=inventory_item.condition,
                sleeve_condition=inventory_item.sleeve_condition,
                price=inventory_item.price,
                location=inventory_item.location,
            )
            db.session.commit()
            return {
                "success": True,
                "found": True,
                "condition": inventory_item.condition,
                "price": inventory_item.price,
            }
        else:
            # Clear inventory data if no longer listed
            if release.listing_id:
                release.clear_inventory_data()
                db.session.commit()
                return {
                    "success": True,
                    "found": False,
                    "message": "Item no longer listed for sale - inventory data cleared",
                }
            return {
                "success": True,
                "found": False,
                "message": "Item not found in inventory",
            }


def get_inventory_sync_status(user_id: int) -> dict:
    """Get inventory sync status for the UI.

    Args:
        user_id: The user to get status for

    Returns:
        Dict with inventory sync info
    """
    # Count releases with inventory data
    releases_with_inventory = Release.query.filter(
        Release.user_id == user_id,
        Release.listing_id.isnot(None),
    ).count()

    # Get most recent inventory sync time
    latest_sync = db.session.query(
        db.func.max(Release.inventory_synced_at)
    ).filter(
        Release.user_id == user_id,
    ).scalar()

    return {
        "items_synced": releases_with_inventory,
        "last_sync": latest_sync.isoformat() if latest_sync else None,
    }
