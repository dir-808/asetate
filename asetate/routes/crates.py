"""Crate routes - managing crates and their contents."""

from flask import Blueprint, render_template, request, jsonify

from asetate import db
from asetate.models import Crate, Release, Track, crate_releases, crate_tracks

bp = Blueprint("crates", __name__)


@bp.route("/")
def list_crates():
    """List all crates (hierarchical view)."""
    # Get top-level crates (no parent)
    top_level = (
        Crate.query.filter(Crate.parent_id.is_(None))
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
    total_crates = Crate.query.count()

    return render_template("crates/list.html", crate_tree=crate_tree, total_crates=total_crates)


@bp.route("/", methods=["POST"])
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
        parent = Crate.query.get(parent_id)
        if not parent:
            return jsonify({"error": "Parent crate not found"}), 404

    # Check for duplicate name within same parent
    existing = Crate.query.filter_by(name=name, parent_id=parent_id).first()
    if existing:
        return jsonify({"error": "A crate with this name already exists"}), 409

    crate = Crate(
        name=name,
        parent_id=parent_id,
        description=data.get("description", "").strip() or None,
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
            },
        }
    )


@bp.route("/<int:crate_id>")
def view_crate(crate_id: int):
    """View a crate and its contents (releases and tracks)."""
    crate = Crate.query.get_or_404(crate_id)

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

    return render_template(
        "crates/detail.html",
        crate=crate,
        releases=releases,
        direct_tracks=direct_tracks,
        children=children,
        breadcrumbs=breadcrumbs,
    )


@bp.route("/<int:crate_id>", methods=["PATCH"])
def update_crate(crate_id: int):
    """Update a crate's name or description."""
    crate = Crate.query.get_or_404(crate_id)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        # Check for duplicate
        existing = Crate.query.filter(
            Crate.name == name, Crate.parent_id == crate.parent_id, Crate.id != crate.id
        ).first()
        if existing:
            return jsonify({"error": "A crate with this name already exists"}), 409
        crate.name = name

    if "description" in data:
        crate.description = data["description"].strip() or None

    db.session.commit()

    return jsonify({"status": "ok", "crate": {"id": crate.id, "name": crate.name}})


@bp.route("/<int:crate_id>", methods=["DELETE"])
def delete_crate(crate_id: int):
    """Delete a crate (and its children)."""
    crate = Crate.query.get_or_404(crate_id)
    db.session.delete(crate)
    db.session.commit()
    return jsonify({"status": "deleted"})


@bp.route("/<int:crate_id>/releases", methods=["POST"])
def add_release_to_crate(crate_id: int):
    """Add a release to a crate."""
    crate = Crate.query.get_or_404(crate_id)

    data = request.get_json()
    if not data or not data.get("release_id"):
        return jsonify({"error": "release_id is required"}), 400

    release = Release.query.get(data["release_id"])
    if not release:
        return jsonify({"error": "Release not found"}), 404

    if release in crate.releases:
        return jsonify({"error": "Release already in crate"}), 409

    crate.releases.append(release)
    db.session.commit()

    return jsonify({"status": "added", "release_id": release.id, "crate_id": crate.id})


@bp.route("/<int:crate_id>/releases/<int:release_id>", methods=["DELETE"])
def remove_release_from_crate(crate_id: int, release_id: int):
    """Remove a release from a crate."""
    crate = Crate.query.get_or_404(crate_id)
    release = Release.query.get_or_404(release_id)

    if release not in crate.releases:
        return jsonify({"error": "Release not in crate"}), 404

    crate.releases.remove(release)
    db.session.commit()

    return jsonify({"status": "removed"})


@bp.route("/<int:crate_id>/tracks", methods=["POST"])
def add_track_to_crate(crate_id: int):
    """Add an individual track to a crate."""
    crate = Crate.query.get_or_404(crate_id)

    data = request.get_json()
    if not data or not data.get("track_id"):
        return jsonify({"error": "track_id is required"}), 400

    track = Track.query.get(data["track_id"])
    if not track:
        return jsonify({"error": "Track not found"}), 404

    if track in crate.tracks:
        return jsonify({"error": "Track already in crate"}), 409

    crate.tracks.append(track)
    db.session.commit()

    return jsonify({"status": "added", "track_id": track.id, "crate_id": crate.id})


@bp.route("/<int:crate_id>/tracks/<int:track_id>", methods=["DELETE"])
def remove_track_from_crate(crate_id: int, track_id: int):
    """Remove a track from a crate."""
    crate = Crate.query.get_or_404(crate_id)
    track = Track.query.get_or_404(track_id)

    if track not in crate.tracks:
        return jsonify({"error": "Track not in crate"}), 404

    crate.tracks.remove(track)
    db.session.commit()

    return jsonify({"status": "removed"})


@bp.route("/api/list")
def api_list_crates():
    """Get all crates as flat JSON list (for dropdowns/selectors)."""
    crates = Crate.query.order_by(Crate.name).all()

    return jsonify(
        {
            "crates": [
                {
                    "id": c.id,
                    "name": c.name,
                    "full_path": c.full_path,
                    "parent_id": c.parent_id,
                    "depth": c.depth,
                }
                for c in crates
            ]
        }
    )


@bp.route("/api/for-release/<int:release_id>")
def api_crates_for_release(release_id: int):
    """Get crates that contain a specific release."""
    release = Release.query.get_or_404(release_id)
    crate_ids = [c.id for c in release.crates]
    return jsonify({"crate_ids": crate_ids})


@bp.route("/api/for-track/<int:track_id>")
def api_crates_for_track(track_id: int):
    """Get crates that contain a specific track."""
    track = Track.query.get_or_404(track_id)
    crate_ids = [c.id for c in track.crates]
    return jsonify({"crate_ids": crate_ids})
