"""Tag routes - managing tags for track categorization."""

from flask import Blueprint, request, jsonify

from asetate import db
from asetate.models import Tag, Track

bp = Blueprint("tags", __name__)


@bp.route("/")
def list_tags():
    """List all tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify({
        "tags": [
            {
                "id": t.id,
                "name": t.name,
                "color": t.color,
                "track_count": t.track_count,
            }
            for t in tags
        ]
    })


@bp.route("/", methods=["POST"])
def create_tag():
    """Create a new tag."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    name = data["name"].strip().lower()
    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400

    # Check for duplicate
    existing = Tag.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "A tag with this name already exists"}), 409

    tag = Tag(
        name=name,
        color=data.get("color", "#E07A5F"),  # Default to primary color
    )
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        "status": "created",
        "tag": {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
        }
    })


@bp.route("/<int:tag_id>", methods=["PATCH"])
def update_tag(tag_id: int):
    """Update a tag's name or color."""
    tag = Tag.query.get_or_404(tag_id)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        name = data["name"].strip().lower()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        # Check for duplicate
        existing = Tag.query.filter(Tag.name == name, Tag.id != tag.id).first()
        if existing:
            return jsonify({"error": "A tag with this name already exists"}), 409
        tag.name = name

    if "color" in data:
        tag.color = data["color"]

    db.session.commit()

    return jsonify({
        "status": "ok",
        "tag": {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
        }
    })


@bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id: int):
    """Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify({"status": "deleted"})


@bp.route("/track/<int:track_id>")
def get_track_tags(track_id: int):
    """Get all tags for a track."""
    track = Track.query.get_or_404(track_id)
    return jsonify({
        "track_id": track.id,
        "tags": [
            {
                "id": t.id,
                "name": t.name,
                "color": t.color,
            }
            for t in track.tags
        ]
    })


@bp.route("/track/<int:track_id>", methods=["POST"])
def add_tag_to_track(track_id: int):
    """Add a tag to a track (creates tag if it doesn't exist)."""
    track = Track.query.get_or_404(track_id)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Can add by tag_id or by name
    if data.get("tag_id"):
        tag = Tag.query.get(data["tag_id"])
        if not tag:
            return jsonify({"error": "Tag not found"}), 404
    elif data.get("name"):
        name = data["name"].strip().lower()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        # Find or create tag
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name, color=data.get("color", "#E07A5F"))
            db.session.add(tag)
            db.session.flush()  # Get the ID
    else:
        return jsonify({"error": "Either tag_id or name is required"}), 400

    if tag in track.tags:
        return jsonify({"error": "Tag already on track"}), 409

    track.tags.append(tag)
    db.session.commit()

    return jsonify({
        "status": "added",
        "tag": {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
        }
    })


@bp.route("/track/<int:track_id>/<int:tag_id>", methods=["DELETE"])
def remove_tag_from_track(track_id: int, tag_id: int):
    """Remove a tag from a track."""
    track = Track.query.get_or_404(track_id)
    tag = Tag.query.get_or_404(tag_id)

    if tag not in track.tags:
        return jsonify({"error": "Tag not on track"}), 404

    track.tags.remove(tag)
    db.session.commit()

    return jsonify({"status": "removed"})


@bp.route("/search")
def search_tags():
    """Search tags by name (for autocomplete)."""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"tags": []})

    tags = Tag.query.filter(Tag.name.ilike(f"%{query}%")).order_by(Tag.name).limit(10).all()
    return jsonify({
        "tags": [
            {
                "id": t.id,
                "name": t.name,
                "color": t.color,
            }
            for t in tags
        ]
    })
