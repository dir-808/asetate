"""Backup service - export/import user data for portability and backup."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from asetate import db
from asetate.models import Release, Track, Crate, Tag, crate_releases, crate_tracks, track_tags


# Current backup format version
BACKUP_VERSION = 1


class BackupService:
    """Service for exporting and importing user data.

    Exports all user-created data (DJ metadata, crates, tags) in a portable
    JSON format. The format is keyed by Discogs IDs so data can be restored
    after a fresh collection sync.
    """

    def __init__(self, user_id: int):
        """Initialize backup service for a user.

        Args:
            user_id: The user ID to backup/restore for
        """
        self.user_id = user_id

    def export_data(self) -> dict[str, Any]:
        """Export all user data to a dictionary.

        Returns:
            Dictionary containing all exportable user data
        """
        return {
            "version": BACKUP_VERSION,
            "exported_at": datetime.utcnow().isoformat(),
            "tracks": self._export_tracks(),
            "releases": self._export_releases(),
            "crates": self._export_crates(),
            "tags": self._export_tags(),
        }

    def export_to_json(self, pretty: bool = True) -> str:
        """Export all user data to JSON string.

        Args:
            pretty: If True, format with indentation for readability

        Returns:
            JSON string of exported data
        """
        data = self.export_data()
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def export_to_file(self, filepath: str | Path) -> Path:
        """Export all user data to a JSON file.

        Args:
            filepath: Path to save the backup file

        Returns:
            Path to the saved file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.export_to_json(pretty=True))

        return filepath

    def _export_tracks(self) -> dict[str, Any]:
        """Export track DJ metadata, keyed by discogs_id:position."""
        tracks_data = {}

        # Get all tracks for this user's releases
        tracks = (
            Track.query
            .join(Release)
            .filter(Release.user_id == self.user_id)
            .all()
        )

        for track in tracks:
            # Only export tracks that have user data
            if not self._track_has_user_data(track):
                continue

            # Key format: "discogs_id:position" for matching after re-sync
            key = f"{track.release.discogs_id}:{track.position or ''}"

            track_data = {}
            if track.bpm is not None:
                track_data["bpm"] = track.bpm
            if track.musical_key:
                track_data["musical_key"] = track.musical_key
            if track.camelot:
                track_data["camelot"] = track.camelot
            if track.energy is not None:
                track_data["energy"] = track.energy
            if track.is_playable:
                track_data["is_playable"] = True
            if track.notes:
                track_data["notes"] = track.notes

            # Export tags for this track
            if track.tags:
                track_data["tags"] = [tag.name for tag in track.tags]

            if track_data:
                tracks_data[key] = track_data

        return tracks_data

    def _export_releases(self) -> dict[str, Any]:
        """Export release user corrections, keyed by discogs_id."""
        releases_data = {}

        releases = Release.query.filter_by(user_id=self.user_id).all()

        for release in releases:
            # Only export releases with user corrections
            if not release.user_corrections:
                continue

            releases_data[str(release.discogs_id)] = {
                "user_corrections": release.user_corrections,
            }

        return releases_data

    def _export_crates(self) -> list[dict[str, Any]]:
        """Export crate hierarchy and memberships."""
        crates_data = []

        # Get all crates for this user, ordered by hierarchy
        crates = (
            Crate.query
            .filter_by(user_id=self.user_id)
            .order_by(Crate.parent_id.nulls_first(), Crate.sort_order)
            .all()
        )

        # Build a map of crate IDs to their data for hierarchy resolution
        crate_map = {}

        for crate in crates:
            crate_data = {
                "name": crate.name,
                "description": crate.description,
                "sort_order": crate.sort_order,
                "parent_path": crate.parent.full_path if crate.parent else None,
                "releases": [r.discogs_id for r in crate.releases],
                "tracks": [
                    f"{t.release.discogs_id}:{t.position or ''}"
                    for t in crate.tracks
                ],
            }
            crates_data.append(crate_data)
            crate_map[crate.id] = crate_data

        return crates_data

    def _export_tags(self) -> list[dict[str, Any]]:
        """Export tags with their colors."""
        tags_data = []

        tags = Tag.query.filter_by(user_id=self.user_id).all()

        for tag in tags:
            tag_data = {
                "name": tag.name,
            }
            if tag.color:
                tag_data["color"] = tag.color

            tags_data.append(tag_data)

        return tags_data

    def _track_has_user_data(self, track: Track) -> bool:
        """Check if a track has any user-entered data worth exporting."""
        return any([
            track.bpm is not None,
            track.musical_key is not None,
            track.camelot is not None,
            track.energy is not None,
            track.is_playable,
            track.notes,
            len(track.tags) > 0,
        ])

    # =========================================================================
    # Import methods
    # =========================================================================

    def import_from_json(self, json_str: str) -> dict[str, int]:
        """Import user data from JSON string.

        Args:
            json_str: JSON string containing backup data

        Returns:
            Dictionary with counts of imported items
        """
        data = json.loads(json_str)
        return self.import_data(data)

    def import_from_file(self, filepath: str | Path) -> dict[str, int]:
        """Import user data from a JSON file.

        Args:
            filepath: Path to the backup file

        Returns:
            Dictionary with counts of imported items
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.import_data(data)

    def import_data(self, data: dict[str, Any]) -> dict[str, int]:
        """Import user data from a dictionary.

        Merges imported data with existing data. User data in the import
        takes precedence over existing data.

        Args:
            data: Dictionary containing backup data

        Returns:
            Dictionary with counts of imported/updated items
        """
        version = data.get("version", 1)
        if version > BACKUP_VERSION:
            raise ValueError(f"Backup version {version} is newer than supported version {BACKUP_VERSION}")

        stats = {
            "tags_created": 0,
            "tracks_updated": 0,
            "releases_updated": 0,
            "crates_created": 0,
        }

        # Import tags first (needed for track tag references)
        stats["tags_created"] = self._import_tags(data.get("tags", []))

        # Import track data
        stats["tracks_updated"] = self._import_tracks(data.get("tracks", {}))

        # Import release corrections
        stats["releases_updated"] = self._import_releases(data.get("releases", {}))

        # Import crates
        stats["crates_created"] = self._import_crates(data.get("crates", []))

        db.session.commit()
        return stats

    def _import_tags(self, tags_data: list[dict]) -> int:
        """Import tags, creating new ones as needed."""
        created = 0

        for tag_data in tags_data:
            name = tag_data.get("name")
            if not name:
                continue

            # Check if tag already exists
            existing = Tag.query.filter_by(user_id=self.user_id, name=name).first()
            if existing:
                # Update color if provided
                if "color" in tag_data:
                    existing.color = tag_data["color"]
            else:
                # Create new tag
                tag = Tag(
                    user_id=self.user_id,
                    name=name,
                    color=tag_data.get("color"),
                )
                db.session.add(tag)
                created += 1

        db.session.flush()
        return created

    def _import_tracks(self, tracks_data: dict[str, dict]) -> int:
        """Import track DJ metadata."""
        updated = 0

        for key, track_data in tracks_data.items():
            # Parse key: "discogs_id:position"
            parts = key.split(":", 1)
            if len(parts) != 2:
                continue

            try:
                discogs_id = int(parts[0])
            except ValueError:
                continue
            position = parts[1]

            # Find the track
            track = (
                Track.query
                .join(Release)
                .filter(
                    Release.user_id == self.user_id,
                    Release.discogs_id == discogs_id,
                    Track.position == position,
                )
                .first()
            )

            if not track:
                continue

            # Update track data
            if "bpm" in track_data:
                track.bpm = track_data["bpm"]
            if "musical_key" in track_data:
                track.musical_key = track_data["musical_key"]
            if "camelot" in track_data:
                track.camelot = track_data["camelot"]
            if "energy" in track_data:
                track.energy = track_data["energy"]
            if "is_playable" in track_data:
                track.is_playable = track_data["is_playable"]
            if "notes" in track_data:
                track.notes = track_data["notes"]

            # Update tags
            if "tags" in track_data:
                tag_names = track_data["tags"]
                tags = Tag.query.filter(
                    Tag.user_id == self.user_id,
                    Tag.name.in_(tag_names),
                ).all()
                track.tags = tags

            updated += 1

        return updated

    def _import_releases(self, releases_data: dict[str, dict]) -> int:
        """Import release user corrections."""
        updated = 0

        for discogs_id_str, release_data in releases_data.items():
            try:
                discogs_id = int(discogs_id_str)
            except ValueError:
                continue

            release = Release.query.filter_by(
                user_id=self.user_id,
                discogs_id=discogs_id,
            ).first()

            if not release:
                continue

            if "user_corrections" in release_data:
                release.user_corrections = release_data["user_corrections"]
                updated += 1

        return updated

    def _import_crates(self, crates_data: list[dict]) -> int:
        """Import crates and their memberships."""
        created = 0

        # First pass: create all crates without memberships
        crate_by_path = {}

        for crate_data in crates_data:
            name = crate_data.get("name")
            if not name:
                continue

            parent_path = crate_data.get("parent_path")

            # Find or create parent
            parent = None
            if parent_path:
                parent = crate_by_path.get(parent_path)
                if not parent:
                    # Parent might not exist yet, skip for now
                    continue

            # Check if crate already exists
            existing = Crate.query.filter_by(
                user_id=self.user_id,
                parent_id=parent.id if parent else None,
                name=name,
            ).first()

            if existing:
                crate = existing
            else:
                crate = Crate(
                    user_id=self.user_id,
                    parent_id=parent.id if parent else None,
                    name=name,
                    description=crate_data.get("description"),
                    sort_order=crate_data.get("sort_order", 0),
                )
                db.session.add(crate)
                db.session.flush()
                created += 1

            # Store by full path for parent lookups
            crate_by_path[crate.full_path] = crate

            # Add releases to crate
            for discogs_id in crate_data.get("releases", []):
                release = Release.query.filter_by(
                    user_id=self.user_id,
                    discogs_id=discogs_id,
                ).first()
                if release and release not in crate.releases:
                    crate.releases.append(release)

            # Add tracks to crate
            for track_key in crate_data.get("tracks", []):
                parts = track_key.split(":", 1)
                if len(parts) != 2:
                    continue
                try:
                    discogs_id = int(parts[0])
                except ValueError:
                    continue
                position = parts[1]

                track = (
                    Track.query
                    .join(Release)
                    .filter(
                        Release.user_id == self.user_id,
                        Release.discogs_id == discogs_id,
                        Track.position == position,
                    )
                    .first()
                )
                if track and track not in crate.tracks:
                    crate.tracks.append(track)

        # Second pass: handle crates with parents that weren't found in first pass
        for crate_data in crates_data:
            name = crate_data.get("name")
            parent_path = crate_data.get("parent_path")

            if not name or not parent_path:
                continue

            if f"{parent_path} / {name}" in crate_by_path:
                continue  # Already created

            parent = crate_by_path.get(parent_path)
            if not parent:
                continue  # Still can't find parent

            existing = Crate.query.filter_by(
                user_id=self.user_id,
                parent_id=parent.id,
                name=name,
            ).first()

            if not existing:
                crate = Crate(
                    user_id=self.user_id,
                    parent_id=parent.id,
                    name=name,
                    description=crate_data.get("description"),
                    sort_order=crate_data.get("sort_order", 0),
                )
                db.session.add(crate)
                created += 1

        return created


def get_default_backup_dir() -> Path:
    """Get the default backup directory path."""
    return Path.home() / ".asetate" / "backups"


def create_auto_backup(user_id: int, reason: str = "auto") -> Path | None:
    """Create an automatic backup file.

    Args:
        user_id: The user ID to backup
        reason: Reason for backup (used in filename)

    Returns:
        Path to the backup file, or None if backup failed
    """
    backup_dir = get_default_backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"asetate_backup_{reason}_{timestamp}.json"
    filepath = backup_dir / filename

    try:
        service = BackupService(user_id)
        service.export_to_file(filepath)

        # Clean up old backups (keep last 10)
        _cleanup_old_backups(backup_dir, keep=10)

        return filepath
    except Exception:
        return None


def _cleanup_old_backups(backup_dir: Path, keep: int = 10):
    """Remove old backup files, keeping the most recent ones.

    Args:
        backup_dir: Directory containing backups
        keep: Number of recent backups to keep
    """
    backups = sorted(
        backup_dir.glob("asetate_backup_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for old_backup in backups[keep:]:
        try:
            old_backup.unlink()
        except Exception:
            pass
