"""Crate routes - managing crates and their contents."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from asetate import db
from asetate.models import Crate, Release, Track, crate_releases, crate_tracks
from asetate.models.crate import CRATE_COLORS, CRATE_ICONS

bp = Blueprint("crates", __name__)


@bp.route("/")
@login_required
def list_crates():
    """List all crates (hierarchical view)."""
    # Get top-level crates (no parent) for current user
    top_level = (
        Crate.query.filter(
            Crate.user_id == current_user.id,
            Crate.parent_id.is_(None)
        )
        .order_by(Crate.sort_order, Crate.name)
        .all()
    )

    # Build hierarchical structure
    def build_tree(crate):
        children = crate.children.order_by(Crate.sort_order, Crate.name).all()
        return {
            "crate": crate,
            "children": [build_tree(c) for c in children],
            "release_count": len(crate.releases),
            "track_count": len(crate.tracks),
        }

    crate_tree = [build_tree(c) for c in top_level]
    total_crates = Crate.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "crates/list.html",
        crate_tree=crate_tree,
        total_crates=total_crates,
        crate_colors=CRATE_COLORS,
        crate_icons=CRATE_ICONS,
    )


@bp.route("/", methods=["POST"])
@login_required
def create_crate():
    """Create a new crate."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip()
    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400

    parent_id = data.get("parent_id")
    if parent_id:
        # Ensure parent belongs to current user
        parent = Crate.query.filter_by(id=parent_id, user_id=current_user.id).first()
        if not parent:
            return jsonify({"error": "Parent crate not found"}), 404

    # Check for duplicate name within same parent for this user
    existing = Crate.query.filter_by(
        user_id=current_user.id,
        name=name,
        parent_id=parent_id
    ).first()
    if existing:
        return jsonify({"error": "A crate with this name already exists"}), 409

    crate = Crate(
        user_id=current_user.id,
        name=name,
        parent_id=parent_id,
        description=data.get("description", "").strip() or None,
        icon=data.get("icon") or None,
        color=data.get("color") or None,
    )
    db.session.add(crate)
    db.session.commit()

    return jsonify(
        {
            "status": "created",
            "crate": {
                "id": crate.id,
                "name": crate.name,
                "parent_id": crate.parent_id,
                "description": crate.description,
                "icon": crate.icon,
                "color": crate.color,
            },
        }
    )


@bp.route("/<int:crate_id>")
@login_required
def view_crate(crate_id: int):
    """View a crate and its contents (releases and tracks)."""
    # Ensure crate belongs to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()

    # Get releases in this crate
    releases = crate.releases

    # Get individual tracks in this crate (not via releases)
    direct_tracks = crate.tracks

    # Get child crates
    children = crate.children.order_by(Crate.sort_order, Crate.name).all()

    # Get breadcrumb path
    breadcrumbs = []
    current = crate
    while current:
        breadcrumbs.insert(0, current)
        current = current.parent

    # Get all crates for parent selection (excluding self and descendants)
    def get_descendants(c):
        result = {c.id}
        for child in c.children:
            result |= get_descendants(child)
        return result

    excluded_ids = get_descendants(crate)
    available_parents = Crate.query.filter(
        Crate.user_id == current_user.id,
        ~Crate.id.in_(excluded_ids)
    ).order_by(Crate.name).all()

    return render_template(
        "crates/detail.html",
        crate=crate,
        releases=releases,
        direct_tracks=direct_tracks,
        children=children,
        breadcrumbs=breadcrumbs,
        crate_colors=CRATE_COLORS,
        crate_icons=CRATE_ICONS,
        available_parents=available_parents,
    )


@bp.route("/<int:crate_id>", methods=["PATCH"])
@login_required
def update_crate(crate_id: int):
    """Update a crate's name or description."""
    # Ensure crate belongs to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        # Check for duplicate within same user and parent
        existing = Crate.query.filter(
            Crate.user_id == current_user.id,
            Crate.name == name,
            Crate.parent_id == crate.parent_id,
            Crate.id != crate.id
        ).first()
        if existing:
            return jsonify({"error": "A crate with this name already exists"}), 409
        crate.name = name

    if "description" in data:
        crate.description = data["description"].strip() or None

    if "icon" in data:
        crate.icon = data["icon"] or None

    if "color" in data:
        crate.color = data["color"] or None

    if "parent_id" in data:
        new_parent_id = data["parent_id"]
        if new_parent_id is not None:
            # Validate parent exists and belongs to user
            parent = Crate.query.filter_by(id=new_parent_id, user_id=current_user.id).first()
            if not parent:
                return jsonify({"error": "Parent crate not found"}), 404
            # Prevent setting self or descendants as parent
            def is_descendant(c, target_id):
                if c.id == target_id:
                    return True
                for child in c.children:
                    if is_descendant(child, target_id):
                        return True
                return False
            if is_descendant(crate, new_parent_id):
                return jsonify({"error": "Cannot set a descendant as parent"}), 400
        crate.parent_id = new_parent_id

    db.session.commit()

    return jsonify({
        "status": "ok",
        "crate": {
            "id": crate.id,
            "name": crate.name,
            "icon": crate.icon,
            "color": crate.color,
        }
    })


@bp.route("/<int:crate_id>", methods=["DELETE"])
@login_required
def delete_crate(crate_id: int):
    """Delete a crate (and its children)."""
    # Ensure crate belongs to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()
    db.session.delete(crate)
    db.session.commit()
    return jsonify({"status": "deleted"})


@bp.route("/<int:crate_id>/releases", methods=["POST"])
@login_required
def add_release_to_crate(crate_id: int):
    """Add a release to a crate."""
    # Ensure crate belongs to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()

    data = request.get_json()
    if not data or not data.get("release_id"):
        return jsonify({"error": "release_id is required"}), 400

    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=data["release_id"],
        user_id=current_user.id
    ).first()
    if not release:
        return jsonify({"error": "Release not found"}), 404

    if release in crate.releases:
        return jsonify({"error": "Release already in crate"}), 409

    crate.releases.append(release)
    db.session.commit()

    return jsonify({"status": "added", "release_id": release.id, "crate_id": crate.id})


@bp.route("/<int:crate_id>/releases/<int:release_id>", methods=["DELETE"])
@login_required
def remove_release_from_crate(crate_id: int, release_id: int):
    """Remove a release from a crate."""
    # Ensure crate and release belong to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()
    release = Release.query.filter_by(id=release_id, user_id=current_user.id).first_or_404()

    if release not in crate.releases:
        return jsonify({"error": "Release not in crate"}), 404

    crate.releases.remove(release)
    db.session.commit()

    return jsonify({"status": "removed"})


@bp.route("/<int:crate_id>/tracks", methods=["POST"])
@login_required
def add_track_to_crate(crate_id: int):
    """Add an individual track to a crate."""
    # Ensure crate belongs to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()

    data = request.get_json()
    if not data or not data.get("track_id"):
        return jsonify({"error": "track_id is required"}), 400

    # Ensure track belongs to a release owned by current user
    track = Track.query.join(Release).filter(
        Track.id == data["track_id"],
        Release.user_id == current_user.id
    ).first()
    if not track:
        return jsonify({"error": "Track not found"}), 404

    if track in crate.tracks:
        return jsonify({"error": "Track already in crate"}), 409

    crate.tracks.append(track)
    db.session.commit()

    return jsonify({"status": "added", "track_id": track.id, "crate_id": crate.id})


@bp.route("/<int:crate_id>/tracks/<int:track_id>", methods=["DELETE"])
@login_required
def remove_track_from_crate(crate_id: int, track_id: int):
    """Remove a track from a crate."""
    # Ensure crate belongs to current user
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()

    # Ensure track belongs to a release owned by current user
    track = Track.query.join(Release).filter(
        Track.id == track_id,
        Release.user_id == current_user.id
    ).first_or_404()

    if track not in crate.tracks:
        return jsonify({"error": "Track not in crate"}), 404

    crate.tracks.remove(track)
    db.session.commit()

    return jsonify({"status": "removed"})


@bp.route("/api/<int:crate_id>")
@login_required
def api_get_crate(crate_id: int):
    """Get a single crate's details for editing."""
    crate = Crate.query.filter_by(id=crate_id, user_id=current_user.id).first_or_404()
    return jsonify({
        "crate": {
            "id": crate.id,
            "name": crate.name,
            "description": crate.description,
            "icon": crate.icon,
            "color": crate.color,
            "color_hex": crate.color_hex,
            "parent_id": crate.parent_id,
        }
    })


@bp.route("/api/list")
@login_required
def api_list_crates():
    """Get all crates as flat JSON list (for dropdowns/selectors)."""
    crates = Crate.query.filter_by(user_id=current_user.id).order_by(Crate.name).all()

    return jsonify(
        {
            "crates": [
                {
                    "id": c.id,
                    "name": c.name,
                    "full_path": c.full_path,
                    "parent_id": c.parent_id,
                    "depth": c.depth,
                    "icon": c.display_icon,
                    "color_hex": c.color_hex,
                }
                for c in crates
            ]
        }
    )


@bp.route("/api/for-release/<int:release_id>")
@login_required
def api_crates_for_release(release_id: int):
    """Get crates that contain a specific release."""
    # Ensure release belongs to current user
    release = Release.query.filter_by(
        id=release_id,
        user_id=current_user.id
    ).first_or_404()
    crate_ids = [c.id for c in release.crates]
    return jsonify({"crate_ids": crate_ids})


@bp.route("/api/for-track/<int:track_id>")
@login_required
def api_crates_for_track(track_id: int):
    """Get crates that contain a specific track."""
    # Ensure track belongs to a release owned by current user
    track = Track.query.join(Release).filter(
        Track.id == track_id,
        Release.user_id == current_user.id
    ).first_or_404()
    crate_ids = [c.id for c in track.crates]
    return jsonify({"crate_ids": crate_ids})
