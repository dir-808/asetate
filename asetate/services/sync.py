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
from asetate.models.inventory_listing import InventoryListing, ListingStatus

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

            # Update current release info for UI feedback
            artist = ", ".join(a.get("name", "") for a in basic_info.get("artists", [])) or "Unknown"
            title = basic_info.get("title", "Untitled")
            progress.current_release_artist = artist[:500]  # Truncate to fit column
            progress.current_release_title = title[:500]

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

    def sync_single_release(self, release: Release) -> None:
        """Sync a single release from Discogs.

        Re-fetches the release data from Discogs and updates local database.
        Preserves user-entered DJ metadata (BPM, key, energy, notes, tags).

        Args:
            release: The Release object to sync
        """
        # Create client based on available credentials
        if self.personal_token:
            self.client = DiscogsClient(personal_token=self.personal_token)
        else:
            self.client = DiscogsClient(
                oauth_token=self.oauth_token,
                oauth_token_secret=self.oauth_token_secret,
            )

        # Get fresh release details from Discogs
        details = self.client.get_release_details(release.discogs_id)

        # Build a minimal collection item structure for parse_release
        item = {
            "basic_information": {
                "id": release.discogs_id,
                "title": details.get("title", release.title),
                "artists": details.get("artists", []),
                "labels": details.get("labels", []),
                "year": details.get("year"),
                "cover_image": details.get("images", [{}])[0].get("uri") if details.get("images") else None,
            }
        }

        release_data = self.client.parse_release(item, details)

        # Update release fields (preserve user data by only updating Discogs fields)
        release.title = release_data.title
        release.artist = release_data.artist
        release.label = release_data.label
        release.year = release_data.year
        release.cover_art_url = release_data.cover_art_url
        release.discogs_uri = release_data.discogs_uri
        release.synced_at = datetime.utcnow()

        # Sync tracks (preserves user DJ metadata)
        self._sync_tracks(release, release_data.tracks)

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
        "current_release_artist": latest.current_release_artist,
        "current_release_title": latest.current_release_title,
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
    """Service for syncing Discogs inventory data to InventoryListing model.

    Supports:
    - Multiple listings per release (different copies at different conditions)
    - Listings not in collection (consignment/flip items)
    - Draft listings (optional)
    - Sold/removed tracking with notifications
    """

    def __init__(
        self,
        user_id: int,
        discogs_username: str,
        oauth_token: str | None = None,
        oauth_token_secret: str | None = None,
        personal_token: str | None = None,
        include_drafts: bool = False,
    ):
        """Initialize the inventory sync service.

        Args:
            user_id: The user ID to sync for.
            discogs_username: Discogs username.
            oauth_token: Discogs OAuth access token (for OAuth mode).
            oauth_token_secret: Discogs OAuth access token secret (for OAuth mode).
            personal_token: Discogs Personal Access Token (for PAT mode).
            include_drafts: Whether to include draft listings.
        """
        self.user_id = user_id
        self.discogs_username = discogs_username
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.personal_token = personal_token
        self.include_drafts = include_drafts
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
                include_drafts=user.include_drafts,
            )
        else:
            return cls(
                user_id=user.id,
                discogs_username=user.discogs_username,
                oauth_token=user.oauth_token,
                oauth_token_secret=user.oauth_token_secret,
                include_drafts=user.include_drafts,
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
        """Sync all inventory data to InventoryListing model.

        Returns:
            Stats dict with counts
        """
        client = self._get_client()

        stats = {
            "created": 0,       # New listings added
            "updated": 0,       # Existing listings updated
            "sold": 0,          # Listings marked as sold
            "removed": 0,       # Listings marked as removed
            "in_collection": 0, # Listings with matching release in collection
            "not_in_collection": 0,  # Listings without matching release
            "total_listings": 0,
        }

        # Track which listing_ids we see
        seen_listing_ids = set()

        # Determine status filter
        status_filter = "all" if self.include_drafts else "for sale"

        # Iterate through all inventory listings
        for listing_data, processed, total in client.iter_inventory(
            self.discogs_username, status=status_filter
        ):
            stats["total_listings"] = total

            listing_id = listing_data.get("id")
            if not listing_id:
                continue

            seen_listing_ids.add(listing_id)

            # Parse listing data
            release_info = listing_data.get("release", {})
            discogs_release_id = release_info.get("id")
            parsed_item = client.parse_inventory_item(listing_data)

            # Determine status
            discogs_status = listing_data.get("status", "For Sale")
            if discogs_status.lower() == "draft":
                status = ListingStatus.DRAFT
            else:
                status = ListingStatus.FOR_SALE

            # Find or create InventoryListing
            inv_listing = InventoryListing.query.filter_by(
                user_id=self.user_id,
                listing_id=listing_id,
            ).first()

            is_new = inv_listing is None
            if is_new:
                inv_listing = InventoryListing(
                    user_id=self.user_id,
                    listing_id=listing_id,
                    discogs_release_id=discogs_release_id,
                )
                db.session.add(inv_listing)
                stats["created"] += 1
            else:
                stats["updated"] += 1

            # Try to link to release in collection
            release = Release.query.filter_by(
                user_id=self.user_id,
                discogs_id=discogs_release_id,
            ).first()

            if release:
                inv_listing.release_id = release.id
                stats["in_collection"] += 1
            else:
                inv_listing.release_id = None
                stats["not_in_collection"] += 1

            # Update listing data
            inv_listing.update_from_discogs(
                condition=parsed_item.condition,
                sleeve_condition=parsed_item.sleeve_condition,
                price=parsed_item.price,
                location=parsed_item.location,
                comments=parsed_item.comments,
                status=status,
                release_title=release_info.get("title"),
                release_artist=release_info.get("artist"),
            )

            # Also update the Release model for backwards compatibility
            if release:
                release.update_inventory_data(
                    listing_id=listing_id,
                    condition=parsed_item.condition,
                    sleeve_condition=parsed_item.sleeve_condition,
                    price=parsed_item.price,
                    location=parsed_item.location,
                )

        # Mark listings no longer in inventory as sold/removed
        active_listings = InventoryListing.query.filter(
            InventoryListing.user_id == self.user_id,
            InventoryListing.status.in_([ListingStatus.FOR_SALE, ListingStatus.DRAFT]),
            InventoryListing.listing_id.notin_(seen_listing_ids) if seen_listing_ids else True,
        ).all()

        for inv_listing in active_listings:
            # Mark as sold (most common reason for disappearing)
            inv_listing.mark_sold()
            stats["sold"] += 1

            # Clear release inventory data for backwards compatibility
            if inv_listing.release:
                inv_listing.release.clear_inventory_data()

        db.session.commit()
        return stats

    def sync_single_release(self, release_id: int) -> dict:
        """Sync all inventory listings for a single release.

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

        # Search inventory for all listings of this release
        found_listings = []
        status_filter = "all" if self.include_drafts else "for sale"

        for listing_data, _, _ in client.iter_inventory(
            self.discogs_username, status=status_filter
        ):
            release_info = listing_data.get("release", {})
            if release_info.get("id") == release.discogs_id:
                found_listings.append(listing_data)

        if found_listings:
            # Update/create InventoryListing for each found listing
            for listing_data in found_listings:
                listing_id = listing_data.get("id")
                parsed_item = client.parse_inventory_item(listing_data)

                discogs_status = listing_data.get("status", "For Sale")
                status = ListingStatus.DRAFT if discogs_status.lower() == "draft" else ListingStatus.FOR_SALE

                inv_listing = InventoryListing.query.filter_by(
                    user_id=self.user_id,
                    listing_id=listing_id,
                ).first()

                if not inv_listing:
                    inv_listing = InventoryListing(
                        user_id=self.user_id,
                        listing_id=listing_id,
                        discogs_release_id=release.discogs_id,
                        release_id=release.id,
                    )
                    db.session.add(inv_listing)

                inv_listing.update_from_discogs(
                    condition=parsed_item.condition,
                    sleeve_condition=parsed_item.sleeve_condition,
                    price=parsed_item.price,
                    location=parsed_item.location,
                    comments=parsed_item.comments,
                    status=status,
                    release_title=release.title,
                    release_artist=release.artist,
                )

            # Update release with first listing for backwards compatibility
            first = found_listings[0]
            first_parsed = client.parse_inventory_item(first)
            release.update_inventory_data(
                listing_id=first.get("id"),
                condition=first_parsed.condition,
                sleeve_condition=first_parsed.sleeve_condition,
                price=first_parsed.price,
                location=first_parsed.location,
            )

            db.session.commit()

            return {
                "success": True,
                "found": True,
                "listings_count": len(found_listings),
                "condition": first_parsed.condition,
                "price": first_parsed.price,
            }
        else:
            # Mark all active listings for this release as sold
            active_listings = InventoryListing.query.filter(
                InventoryListing.user_id == self.user_id,
                InventoryListing.release_id == release.id,
                InventoryListing.status.in_([ListingStatus.FOR_SALE, ListingStatus.DRAFT]),
            ).all()

            sold_count = 0
            for inv_listing in active_listings:
                inv_listing.mark_sold()
                sold_count += 1

            # Clear release inventory data
            if release.listing_id:
                release.clear_inventory_data()

            db.session.commit()

            if sold_count > 0:
                return {
                    "success": True,
                    "found": False,
                    "sold_count": sold_count,
                    "message": f"{sold_count} listing(s) marked as sold",
                }

            return {
                "success": True,
                "found": False,
                "message": "No listings found for this release",
            }

    def dismiss_notification(self, listing_id: int) -> bool:
        """Dismiss the sold/removed notification for a listing.

        Args:
            listing_id: The InventoryListing.id

        Returns:
            True if successful
        """
        inv_listing = InventoryListing.query.filter_by(
            id=listing_id,
            user_id=self.user_id,
        ).first()

        if inv_listing:
            inv_listing.dismiss_notification()
            db.session.commit()
            return True
        return False


def get_inventory_sync_status(user_id: int) -> dict:
    """Get inventory sync status for the UI.

    Args:
        user_id: The user to get status for

    Returns:
        Dict with inventory sync info
    """
    # Count active listings
    active_listings = InventoryListing.query.filter(
        InventoryListing.user_id == user_id,
        InventoryListing.status.in_([ListingStatus.FOR_SALE, ListingStatus.DRAFT]),
    ).count()

    # Count listings needing attention (sold/removed, not dismissed)
    needs_attention = InventoryListing.query.filter(
        InventoryListing.user_id == user_id,
        InventoryListing.status.in_([ListingStatus.SOLD, ListingStatus.REMOVED]),
        InventoryListing.notification_dismissed == False,
    ).count()

    # Get most recent sync time
    latest_sync = db.session.query(
        db.func.max(InventoryListing.synced_at)
    ).filter(
        InventoryListing.user_id == user_id,
    ).scalar()

    return {
        "items_synced": active_listings,
        "needs_attention": needs_attention,
        "last_sync": latest_sync.isoformat() if latest_sync else None,
    }


def get_inventory_notifications(user_id: int) -> list[dict]:
    """Get inventory listings that need attention (sold/removed).

    Args:
        user_id: The user to get notifications for

    Returns:
        List of notification dicts
    """
    listings = InventoryListing.query.filter(
        InventoryListing.user_id == user_id,
        InventoryListing.status.in_([ListingStatus.SOLD, ListingStatus.REMOVED]),
        InventoryListing.notification_dismissed == False,
    ).order_by(InventoryListing.sold_at.desc()).all()

    return [
        {
            "id": listing.id,
            "listing_id": listing.listing_id,
            "status": listing.status,
            "title": listing.display_title,
            "artist": listing.display_artist,
            "condition": listing.condition,
            "price": listing.price,
            "sold_at": listing.sold_at.isoformat() if listing.sold_at else None,
            "removed_at": listing.removed_at.isoformat() if listing.removed_at else None,
            "release_id": listing.release_id,
            "in_collection": listing.is_in_collection,
        }
        for listing in listings
    ]
