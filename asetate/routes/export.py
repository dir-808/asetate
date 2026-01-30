"""Export routes - CSV export for label printing."""

import csv
import io
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import or_

from asetate import db
from asetate.models import Release, Track, Crate, Tag, ExportPreset

bp = Blueprint("export", __name__)


def build_track_query(user_id: int, filters: dict):
    """Build a track query based on filter criteria.

    Args:
        user_id: The user to filter by
        filters: Dictionary with filter options:
            - crate_id: Filter by crate (includes all tracks from releases in crate)
            - bpm_min: Minimum BPM
            - bpm_max: Maximum BPM
            - energy_min: Minimum energy
            - energy_max: Maximum energy
            - playable_only: Only playable tracks
            - has_bpm: Only tracks with BPM set
            - has_key: Only tracks with key set
            - tags: List of tag names to filter by
            - search: Text search on track/release/artist

    Returns:
        SQLAlchemy query for Track
    """
    query = Track.query.join(Release).filter(
        Release.user_id == user_id,
        Release.discogs_removed_at.is_(None)
    )

    # Crate filter
    crate_id = filters.get("crate_id")
    if crate_id:
        # Ensure crate belongs to user
        crate = Crate.query.filter_by(id=crate_id, user_id=user_id).first()
        if crate:
            # Get all track IDs from crate (direct tracks + tracks from releases)
            track_ids = set()
            for track in crate.tracks:
                track_ids.add(track.id)
            for release in crate.releases:
                for track in release.tracks:
                    track_ids.add(track.id)
            if track_ids:
                query = query.filter(Track.id.in_(track_ids))
            else:
                # No tracks in crate, return empty
                query = query.filter(Track.id == -1)

    # BPM range
    bpm_min = filters.get("bpm_min")
    bpm_max = filters.get("bpm_max")
    if bpm_min is not None:
        query = query.filter(Track.bpm >= bpm_min)
    if bpm_max is not None:
        query = query.filter(Track.bpm <= bpm_max)

    # Energy range
    energy_min = filters.get("energy_min")
    energy_max = filters.get("energy_max")
    if energy_min is not None:
        query = query.filter(Track.energy >= energy_min)
    if energy_max is not None:
        query = query.filter(Track.energy <= energy_max)

    # Playable only
    if filters.get("playable_only"):
        query = query.filter(Track.is_playable == True)

    # Has BPM
    if filters.get("has_bpm"):
        query = query.filter(Track.bpm.isnot(None))

    # Has key
    if filters.get("has_key"):
        query = query.filter(
            or_(Track.musical_key.isnot(None), Track.camelot.isnot(None))
        )

    # Tags filter (tracks must have ALL specified tags)
    tags = filters.get("tags", [])
    if tags:
        for tag_name in tags:
            # Filter by user's tags
            tag = Tag.query.filter_by(user_id=user_id, name=tag_name.lower().strip()).first()
            if tag:
                query = query.filter(Track.tags.contains(tag))
            else:
                # Tag doesn't exist for this user, no matches
                query = query.filter(Track.id == -1)
                break

    # Key filter
    key = filters.get("key")
    if key:
        query = query.filter(
            or_(
                Track.camelot.ilike(f"%{key}%"),
                Track.musical_key.ilike(f"%{key}%")
            )
        )

    # Text search
    search = filters.get("search", "").strip()
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Track.title.ilike(search_term),
                Release.title.ilike(search_term),
                Release.artist.ilike(search_term),
            )
        )

    # Order by release artist, then release title, then track position
    query = query.order_by(Release.artist, Release.title, Track.position)

    return query


def track_to_dict(track: Track, columns: list[str]) -> dict:
    """Convert a track to a dictionary with only specified columns."""
    release = track.release
    data = {}

    column_map = {
        "artist": lambda: release.display_artist,
        "release_title": lambda: release.display_title,
        "track_title": lambda: track.title,
        "position": lambda: track.display_position,
        "label": lambda: release.label or "",
        "year": lambda: str(release.year) if release.year else "",
        "bpm": lambda: str(track.bpm) if track.bpm else "",
        "musical_key": lambda: track.musical_key or "",
        "camelot": lambda: track.camelot or "",
        "energy": lambda: str(track.energy) if track.energy else "",
        "duration": lambda: track.display_duration,
        "notes": lambda: track.notes or "",
        "tags": lambda: ", ".join(t.name for t in track.tags),
        "crates": lambda: ", ".join(c.name for c in track.crates),
        "release_url": lambda: release.discogs_uri or f"https://www.discogs.com/release/{release.discogs_id}",
        "discogs_id": lambda: str(release.discogs_id),
    }

    for col in columns:
        if col in column_map:
            data[col] = column_map[col]()

    return data


@bp.route("/")
@login_required
def export_page():
    """Export configuration page."""
    # Get user's crates for dropdown
    crates = Crate.query.filter_by(user_id=current_user.id).order_by(Crate.name).all()

    # Get user's tags for filter
    tags = Tag.query.filter_by(user_id=current_user.id).order_by(Tag.name).all()

    # Get user's presets
    presets = ExportPreset.query.filter_by(user_id=current_user.id).order_by(ExportPreset.name).all()

    # Available columns (filter seller columns based on user setting)
    columns = ExportPreset.AVAILABLE_COLUMNS
    seller_columns = [c[0] for c in ExportPreset.SELLER_COLUMNS]
    if not current_user.is_seller_mode:
        columns = [c for c in columns if c[0] not in seller_columns]
    default_columns = ExportPreset.get_default_columns()

    return render_template(
        "export/index.html",
        crates=crates,
        tags=tags,
        presets=presets,
        columns=columns,
        default_columns=default_columns,
        is_seller_mode=current_user.is_seller_mode,
    )


@bp.route("/preview", methods=["POST"])
@login_required
def preview_export():
    """Preview export results based on current filters."""
    data = request.get_json() or {}
    filters = data.get("filters", {})
    columns = data.get("columns", ExportPreset.get_default_columns())
    limit = data.get("limit", 50)  # Preview limit

    # Parse filter values
    parsed_filters = {}

    if filters.get("crate_id"):
        parsed_filters["crate_id"] = int(filters["crate_id"])

    if filters.get("bpm_min"):
        parsed_filters["bpm_min"] = int(filters["bpm_min"])
    if filters.get("bpm_max"):
        parsed_filters["bpm_max"] = int(filters["bpm_max"])

    if filters.get("energy_min"):
        parsed_filters["energy_min"] = int(filters["energy_min"])
    if filters.get("energy_max"):
        parsed_filters["energy_max"] = int(filters["energy_max"])

    if filters.get("playable_only"):
        parsed_filters["playable_only"] = True

    if filters.get("has_bpm"):
        parsed_filters["has_bpm"] = True

    if filters.get("has_key"):
        parsed_filters["has_key"] = True

    if filters.get("key"):
        parsed_filters["key"] = filters["key"]

    if filters.get("tags"):
        # Tags can be comma-separated string or list
        tags = filters["tags"]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        parsed_filters["tags"] = tags

    if filters.get("search"):
        parsed_filters["search"] = filters["search"]

    query = build_track_query(current_user.id, parsed_filters)
    total_count = query.count()
    tracks = query.limit(limit).all()

    track_data = [track_to_dict(t, columns) for t in tracks]

    return jsonify({
        "tracks": track_data,
        "count": total_count,
        "preview_count": len(track_data),
        "columns": columns,
    })


@bp.route("/download", methods=["POST"])
@login_required
def download_csv():
    """Generate and download CSV based on filters."""
    data = request.get_json() or {}
    filters = data.get("filters", {})
    columns = data.get("columns", ExportPreset.get_default_columns())

    # Parse filters same as preview
    parsed_filters = {}

    if filters.get("crate_id"):
        parsed_filters["crate_id"] = int(filters["crate_id"])

    if filters.get("bpm_min"):
        parsed_filters["bpm_min"] = int(filters["bpm_min"])
    if filters.get("bpm_max"):
        parsed_filters["bpm_max"] = int(filters["bpm_max"])

    if filters.get("energy_min"):
        parsed_filters["energy_min"] = int(filters["energy_min"])
    if filters.get("energy_max"):
        parsed_filters["energy_max"] = int(filters["energy_max"])

    if filters.get("playable_only"):
        parsed_filters["playable_only"] = True

    if filters.get("has_bpm"):
        parsed_filters["has_bpm"] = True

    if filters.get("has_key"):
        parsed_filters["has_key"] = True

    if filters.get("key"):
        parsed_filters["key"] = filters["key"]

    if filters.get("tags"):
        tags = filters["tags"]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        parsed_filters["tags"] = tags

    if filters.get("search"):
        parsed_filters["search"] = filters["search"]

    query = build_track_query(current_user.id, parsed_filters)
    tracks = query.all()

    # Column labels
    column_labels = dict(ExportPreset.AVAILABLE_COLUMNS)

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([column_labels.get(col, col) for col in columns])

    # Data rows
    for track in tracks:
        row_data = track_to_dict(track, columns)
        writer.writerow([row_data.get(col, "") for col in columns])

    csv_content = output.getvalue()

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"asetate_export_{timestamp}.csv"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )


@bp.route("/presets", methods=["GET"])
@login_required
def list_presets():
    """List saved export presets for current user."""
    presets = ExportPreset.query.filter_by(user_id=current_user.id).order_by(ExportPreset.name).all()
    return jsonify({
        "presets": [
            {
                "id": p.id,
                "name": p.name,
                "filters": p.filters,
                "columns": p.columns,
            }
            for p in presets
        ]
    })


@bp.route("/presets", methods=["POST"])
@login_required
def save_preset():
    """Save current export configuration as a preset."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()
    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400

    # Check for duplicate name for this user
    existing = ExportPreset.query.filter_by(user_id=current_user.id, name=name).first()
    if existing:
        # Update existing preset
        existing.filters = data.get("filters", {})
        existing.columns = data.get("columns", ExportPreset.get_default_columns())
        db.session.commit()
        return jsonify({
            "status": "updated",
            "preset": {
                "id": existing.id,
                "name": existing.name,
            }
        })

    # Create new preset
    preset = ExportPreset(
        user_id=current_user.id,
        name=name,
        filters=data.get("filters", {}),
        columns=data.get("columns", ExportPreset.get_default_columns()),
    )
    db.session.add(preset)
    db.session.commit()

    return jsonify({
        "status": "created",
        "preset": {
            "id": preset.id,
            "name": preset.name,
        }
    })


@bp.route("/presets/<int:preset_id>", methods=["GET"])
@login_required
def get_preset(preset_id: int):
    """Get a specific preset."""
    # Ensure preset belongs to current user
    preset = ExportPreset.query.filter_by(id=preset_id, user_id=current_user.id).first_or_404()
    return jsonify({
        "id": preset.id,
        "name": preset.name,
        "filters": preset.filters,
        "columns": preset.columns,
    })


@bp.route("/presets/<int:preset_id>", methods=["DELETE"])
@login_required
def delete_preset(preset_id: int):
    """Delete a preset."""
    # Ensure preset belongs to current user
    preset = ExportPreset.query.filter_by(id=preset_id, user_id=current_user.id).first_or_404()
    db.session.delete(preset)
    db.session.commit()
    return jsonify({"status": "deleted"})
