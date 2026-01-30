"""Sync routes - Discogs collection synchronization."""

from flask import Blueprint, render_template, jsonify

bp = Blueprint("sync", __name__)


@bp.route("/")
def sync_status():
    """View current sync status and history."""
    # TODO: Implement sync status page
    return render_template("sync/status.html")


@bp.route("/start", methods=["POST"])
def start_sync():
    """Start a new Discogs collection sync."""
    # TODO: Implement sync start
    return jsonify({"status": "started"})


@bp.route("/pause", methods=["POST"])
def pause_sync():
    """Pause the current sync."""
    # TODO: Implement sync pause
    return jsonify({"status": "paused"})


@bp.route("/resume", methods=["POST"])
def resume_sync():
    """Resume a paused sync."""
    # TODO: Implement sync resume
    return jsonify({"status": "resumed"})
