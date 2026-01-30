"""Sync routes - Discogs collection synchronization."""

import threading

from flask import Blueprint, render_template, jsonify, current_app

from asetate import db
from asetate.services import SyncService, get_sync_status, DiscogsAuthError, DiscogsRateLimitError
from asetate.models import SyncProgress
from asetate.models.sync_progress import SyncStatus

bp = Blueprint("sync", __name__)

# Simple in-memory lock to prevent concurrent syncs
_sync_lock = threading.Lock()
_sync_thread: threading.Thread | None = None


@bp.route("/")
def sync_page():
    """View current sync status and history."""
    status = get_sync_status()
    return render_template("sync/status.html", sync_status=status)


@bp.route("/status")
def sync_status_api():
    """Get current sync status as JSON (for polling)."""
    return jsonify(get_sync_status())


@bp.route("/start", methods=["POST"])
def start_sync():
    """Start a new Discogs collection sync.

    Runs in a background thread to avoid blocking the request.
    """
    global _sync_thread

    # Check if already syncing
    if _sync_thread and _sync_thread.is_alive():
        return jsonify({"error": "Sync already in progress"}), 409

    # Check for valid token
    if not current_app.config.get("DISCOGS_USER_TOKEN"):
        return jsonify({"error": "Discogs token not configured"}), 400

    # Start sync in background thread
    def run_sync():
        with current_app.app_context():
            try:
                service = SyncService()
                service.start_sync(resume=False)
            except DiscogsAuthError as e:
                # Update progress with error
                progress = SyncProgress.get_latest()
                if progress:
                    progress.fail(f"Authentication failed: {e}")
                    db.session.commit()
            except DiscogsRateLimitError as e:
                # Already handled in service (paused)
                pass
            except Exception as e:
                progress = SyncProgress.get_latest()
                if progress:
                    progress.fail(str(e))
                    db.session.commit()

    _sync_thread = threading.Thread(target=run_sync, daemon=True)
    _sync_thread.start()

    return jsonify({"status": "started", "message": "Sync started in background"})


@bp.route("/resume", methods=["POST"])
def resume_sync():
    """Resume a paused or failed sync."""
    global _sync_thread

    # Check if already syncing
    if _sync_thread and _sync_thread.is_alive():
        return jsonify({"error": "Sync already in progress"}), 409

    # Check if there's something to resume
    latest = SyncProgress.get_latest()
    if not latest or not latest.can_resume:
        return jsonify({"error": "No sync to resume"}), 400

    # Start sync in background thread
    def run_sync():
        with current_app.app_context():
            try:
                service = SyncService()
                service.start_sync(resume=True)
            except DiscogsRateLimitError:
                pass  # Already handled
            except Exception as e:
                progress = SyncProgress.get_latest()
                if progress:
                    progress.fail(str(e))
                    db.session.commit()

    _sync_thread = threading.Thread(target=run_sync, daemon=True)
    _sync_thread.start()

    return jsonify({"status": "resumed", "message": "Sync resumed"})


@bp.route("/cancel", methods=["POST"])
def cancel_sync():
    """Cancel/pause the current sync."""
    latest = SyncProgress.get_latest()
    if latest and latest.is_running:
        latest.pause()
        db.session.commit()
        return jsonify({"status": "paused", "message": "Sync paused"})

    return jsonify({"error": "No active sync to cancel"}), 400


@bp.route("/history")
def sync_history():
    """Get sync history."""
    history = SyncProgress.query.order_by(SyncProgress.created_at.desc()).limit(10).all()

    return jsonify(
        {
            "history": [
                {
                    "id": s.id,
                    "status": s.status,
                    "total": s.total_releases,
                    "added": s.added_releases,
                    "updated": s.updated_releases,
                    "removed": s.removed_releases,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in history
            ]
        }
    )
