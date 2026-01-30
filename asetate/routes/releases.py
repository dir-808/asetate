"""Release routes - viewing and managing vinyl releases."""

from flask import Blueprint, render_template, request, jsonify

bp = Blueprint("releases", __name__)


@bp.route("/")
def list_releases():
    """List all releases in the collection."""
    # TODO: Implement release listing with pagination and filtering
    return render_template("releases/list.html")


@bp.route("/<int:release_id>")
def view_release(release_id: int):
    """View a single release and its tracks."""
    # TODO: Implement release detail view
    return render_template("releases/detail.html", release_id=release_id)


@bp.route("/<int:release_id>/tracks/<int:track_id>", methods=["PATCH"])
def update_track(release_id: int, track_id: int):
    """Update DJ metadata for a track (BPM, key, energy, playable, notes)."""
    # TODO: Implement track update
    return jsonify({"status": "ok"})
