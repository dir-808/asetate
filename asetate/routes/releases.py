"""Release routes - viewing and managing vinyl releases."""

from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import or_

from asetate import db, limiter
from asetate.models import Release, Track, Crate

bp = Blueprint("releases", __name__)


def get_release_crate_data(release_ids, user_id):
    """Get crate icons and IDs for a list of releases."""
    if not release_ids:
        return {}

    from asetate.models.crate import crate_releases

    # Query crates for these releases with color info
    crate_data = db.session.query(
        crate_releases.c.release_id,
        Crate
    ).join(Crate).filter(
        crate_releases.c.release_id.in_(release_ids),
        Crate.user_id == user_id
    ).all()

    # Group by release with full crate info for icon rendering
    release_crates = {}
    for release_id, crate in crate_data:
        if release_id not in release_crates:
            release_crates[release_id] = {"crates": [], "ids": []}
        release_crates[release_id]["crates"].append({
            "id": crate.id,
            "name": crate.name,
            "icon_url": crate.icon_url,
            "icon_type": crate.icon_type,
            "color_hex": crate.color_hex,
        })
        release_crates[release_id]["ids"].append(crate.id)

    return release_crates


@bp.route("/")
@login_required
def list_releases():
    """List all releases in the user's collection."""
    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 24, type=int)
    search = request.args.get("q", "").strip()
    filter_type = request.args.get("filter", "")
    crate_filter = request.args.get("crate", "")

    # Build base query - filter by user and exclude removed releases
    query = Release.query.filter(
        Release.user_id == current_user.id,
        Release.discogs_removed_at.is_(None)
    )

    # Apply search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Release.title.ilike(search_term),
                Release.artist.ilike(search_term),
                Release.label.ilike(search_term),
            )
        )

    # Apply crate filter
    if crate_filter:
        from asetate.models.crate import crate_releases
        query = query.filter(
            Release.id.in_(
                db.session.query(crate_releases.c.release_id).filter(
                    crate_releases.c.crate_id == int(crate_filter)
                )
            )
        )

    # Apply filters
    if filter_type == "playable":
        # Releases with at least one playable track
        query = query.filter(
            Release.id.in_(
                db.session.query(Track.release_id)
                .join(Release)
                .filter(
                    Release.user_id == current_user.id,
                    Track.is_playable == True
                )
                .distinct()
            )
        )
    elif filter_type == "needs_metadata":
        # Releases with tracks missing BPM or key
        query = query.filter(
            Release.id.in_(
                db.session.query(Track.release_id)
                .join(Release)
                .filter(
                    Release.user_id == current_user.id,
                    or_(Track.bpm.is_(None), Track.musical_key.is_(None)),
                    Track.is_playable == True,
                )
                .distinct()
            )
        )

    # Order by most recently synced
    query = query.order_by(Release.synced_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get crate data for these releases
    release_ids = [r.id for r in pagination.items]
    crate_data = get_release_crate_data(release_ids, current_user.id)

    # Add crate info to releases
    for release in pagination.items:
        release_info = crate_data.get(release.id, {"crates": [], "ids": []})
        release.crate_info = release_info["crates"]
        release.crate_ids = release_info["ids"]

    # Get stats for the header (user-scoped)
    total_releases = Release.query.filter(
        Release.user_id == current_user.id,
        Release.discogs_removed_at.is_(None)
    ).count()
    total_tracks = (
        Track.query.join(Release)
        .filter(
            Release.user_id == current_user.id,
            Release.discogs_removed_at.is_(None)
        )
        .count()
    )
    playable_tracks = (
        Track.query.join(Release)
        .filter(
            Release.user_id == current_user.id,
            Release.discogs_removed_at.is_(None),
            Track.is_playable == True
        )
        .count()
    )

    # Get all crates for the filter dropdown
    available_crates = Crate.query.filter_by(user_id=current_user.id).order_by(Crate.name).all()

    return render_template(
        "releases/list.html",
        releases=pagination.items,
        pagination=pagination,
        search=search,
        filter_type=filter_type,
        crate_filter=crate_filter,
        available_crates=available_crates,
        stats={
            "releases": total_releases,
            "tracks": total_tracks,
            "playable": playable_tracks,
        },
    )


@bp.route("/<int:release_id>")
@login_required
def view_release(release_id: int):
    """View a single release and its tracks."""
    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=release_id,
        user_id=current_user.id
    ).first_or_404()
    tracks = release.tracks.order_by(Track.position).all()

    # Calculate release stats
    playable_count = sum(1 for t in tracks if t.is_playable)
    has_bpm = sum(1 for t in tracks if t.bpm is not None)

    return render_template(
        "releases/detail.html",
        release=release,
        tracks=tracks,
        stats={
            "total": len(tracks),
            "playable": playable_count,
            "has_bpm": has_bpm,
        },
        visible_fields=current_user.visible_track_fields,
    )


@bp.route("/<int:release_id>/panel")
@login_required
def release_panel(release_id: int):
    """Get release details as a partial HTML for side panel loading."""
    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=release_id,
        user_id=current_user.id
    ).first_or_404()
    tracks = release.tracks.order_by(Track.position).all()

    # Calculate release stats
    playable_count = sum(1 for t in tracks if t.is_playable)
    has_bpm = sum(1 for t in tracks if t.bpm is not None)

    return render_template(
        "releases/panel.html",
        release=release,
        tracks=tracks,
        stats={
            "total": len(tracks),
            "playable": playable_count,
            "has_bpm": has_bpm,
        },
    )


@bp.route("/<int:release_id>/tracks/<int:track_id>", methods=["PATCH"])
@login_required
@limiter.limit("300 per hour")
def update_track(release_id: int, track_id: int):
    """Update DJ metadata for a track (BPM, key, energy, playable, notes)."""
    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=release_id,
        user_id=current_user.id
    ).first_or_404()

    track = Track.query.filter_by(id=track_id, release_id=release.id).first_or_404()

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update allowed fields
    if "bpm" in data:
        bpm = data["bpm"]
        if bpm is not None and bpm != "":
            bpm = int(bpm)
            if not (20 <= bpm <= 300):
                return jsonify({"error": "BPM must be between 20 and 300"}), 400
            track.bpm = bpm
        else:
            track.bpm = None

    if "musical_key" in data:
        track.musical_key = data["musical_key"] or None

    if "camelot" in data:
        track.camelot = data["camelot"] or None

    if "energy" in data:
        energy = data["energy"]
        if energy is not None and energy != "":
            energy = int(energy)
            if not (1 <= energy <= 5):
                return jsonify({"error": "Energy must be between 1 and 5"}), 400
            track.energy = energy
        else:
            track.energy = None

    if "is_playable" in data:
        track.is_playable = bool(data["is_playable"])

    if "notes" in data:
        track.notes = data["notes"] or None

    db.session.commit()

    return jsonify(
        {
            "status": "ok",
            "track": {
                "id": track.id,
                "bpm": track.bpm,
                "musical_key": track.musical_key,
                "camelot": track.camelot,
                "energy": track.energy,
                "is_playable": track.is_playable,
                "notes": track.notes,
            },
        }
    )


@bp.route("/<int:release_id>/corrections", methods=["PATCH"])
@login_required
@limiter.limit("300 per hour")
def update_corrections(release_id: int):
    """Update user corrections for a release (local overrides for Discogs data)."""
    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=release_id,
        user_id=current_user.id
    ).first_or_404()

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Initialize corrections dict if needed
    if not release.user_corrections:
        release.user_corrections = {}

    # Only allow correcting specific fields
    allowed_fields = {"title", "artist", "label", "year"}
    for field, value in data.items():
        if field in allowed_fields:
            if value and value.strip():
                release.user_corrections[field] = value.strip()
            elif field in release.user_corrections:
                # Remove correction if empty (revert to Discogs data)
                del release.user_corrections[field]

    db.session.commit()

    return jsonify(
        {
            "status": "ok",
            "corrections": release.user_corrections,
            "discogs_edit_url": release.discogs_edit_url,
        }
    )


@bp.route("/<int:release_id>/notes", methods=["PATCH"])
@login_required
@limiter.limit("300 per hour")
def update_release_notes(release_id: int):
    """Update notes for a release."""
    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=release_id,
        user_id=current_user.id
    ).first_or_404()

    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data provided"}), 400

    if "notes" in data:
        release.notes = data["notes"] or None

    db.session.commit()

    return jsonify({"status": "ok", "notes": release.notes})


@bp.route("/settings/visible-fields", methods=["GET"])
@login_required
def get_visible_fields():
    """Get the user's visible field settings for the tracks table."""
    return jsonify({
        "visible_fields": current_user.visible_track_fields,
        "available_fields": [
            {"id": "position", "label": "Side"},
            {"id": "title", "label": "Title"},
            {"id": "duration", "label": "Length"},
            {"id": "bpm", "label": "BPM"},
            {"id": "key", "label": "Key"},
            {"id": "energy", "label": "Energy"},
            {"id": "tags", "label": "Tags"},
            {"id": "playable", "label": "Playable"},
        ]
    })


@bp.route("/settings/visible-fields", methods=["PATCH"])
@login_required
def update_visible_fields():
    """Update the user's visible field settings for the tracks table."""
    data = request.get_json()
    if data is None or "visible_fields" not in data:
        return jsonify({"error": "visible_fields is required"}), 400

    fields = data["visible_fields"]
    if not isinstance(fields, list):
        return jsonify({"error": "visible_fields must be a list"}), 400

    # Validate fields
    valid_fields = {"position", "title", "duration", "bpm", "key", "energy", "tags", "playable"}
    fields = [f for f in fields if f in valid_fields]

    # Ensure title and playable are always visible (required)
    if "title" not in fields:
        fields.insert(0, "title")
    if "playable" not in fields:
        fields.append("playable")

    current_user.set_visible_track_fields(fields)
    db.session.commit()

    return jsonify({"status": "ok", "visible_fields": fields})
