"""Sync routes - Discogs collection synchronization."""

import threading

from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required, current_user

from asetate import db, limiter
from asetate.services import SyncService, get_sync_status, DiscogsAuthError, DiscogsRateLimitError, create_auto_backup
from asetate.models import SyncProgress
from asetate.models.sync_progress import SyncStatus

bp = Blueprint("sync", __name__)

# Simple in-memory lock to prevent concurrent syncs per user
_sync_threads: dict[int, threading.Thread] = {}


@bp.route("/")
@login_required
def sync_page():
    """View current sync status and history."""
    status = get_sync_status(current_user.id)
    return render_template("sync/status.html", sync_status=status)


@bp.route("/status")
@login_required
def sync_status_api():
    """Get current sync status as JSON (for polling)."""
    return jsonify(get_sync_status(current_user.id))


@bp.route("/start", methods=["POST"])
@login_required
@limiter.limit("5 per hour")
def start_sync():
    """Start a new Discogs collection sync.

    Runs in a background thread to avoid blocking the request.
    """
    user_id = current_user.id

    # Check if already syncing for this user
    if user_id in _sync_threads and _sync_threads[user_id].is_alive():
        return jsonify({"error": "Sync already in progress"}), 409

    # Check for valid credentials
    if not current_user.has_discogs_credentials:
        return jsonify({"error": "Discogs credentials not configured. Go to Settings to add them."}), 400

    # Auto-backup before sync (in case sync overwrites data)
    try:
        create_auto_backup(user_id, reason="pre_sync")
    except Exception as e:
        current_app.logger.warning(f"Auto-backup failed: {e}")

    # Capture credentials for background thread (works for both OAuth and PAT modes)
    discogs_username = current_user.discogs_username
    oauth_token = current_user.oauth_token
    oauth_token_secret = current_user.oauth_token_secret
    personal_token = current_user.personal_token

    # Start sync in background thread
    def run_sync():
        with current_app.app_context():
            try:
                service = SyncService(
                    user_id=user_id,
                    discogs_username=discogs_username,
                    oauth_token=oauth_token,
                    oauth_token_secret=oauth_token_secret,
                    personal_token=personal_token,
                )
                service.start_sync(resume=False)
            except DiscogsAuthError as e:
                # Update progress with error
                progress = SyncProgress.get_latest(user_id=user_id)
                if progress:
                    progress.fail(f"Authentication failed: {e}")
                    db.session.commit()
            except DiscogsRateLimitError as e:
                # Already handled in service (paused)
                pass
            except Exception as e:
                progress = SyncProgress.get_latest(user_id=user_id)
                if progress:
                    progress.fail(str(e))
                    db.session.commit()

    thread = threading.Thread(target=run_sync, daemon=True)
    _sync_threads[user_id] = thread
    thread.start()

    return jsonify({"status": "started", "message": "Sync started in background"})


@bp.route("/resume", methods=["POST"])
@login_required
def resume_sync():
    """Resume a paused or failed sync."""
    user_id = current_user.id

    # Check if already syncing for this user
    if user_id in _sync_threads and _sync_threads[user_id].is_alive():
        return jsonify({"error": "Sync already in progress"}), 409

    # Check for valid credentials
    if not current_user.has_discogs_credentials:
        return jsonify({"error": "Discogs credentials not configured. Go to Settings to add them."}), 400

    # Check if there's something to resume for this user
    latest = SyncProgress.get_latest(user_id=user_id)
    if not latest or not latest.can_resume:
        return jsonify({"error": "No sync to resume"}), 400

    # Capture credentials for background thread (works for both OAuth and PAT modes)
    discogs_username = current_user.discogs_username
    oauth_token = current_user.oauth_token
    oauth_token_secret = current_user.oauth_token_secret
    personal_token = current_user.personal_token

    # Start sync in background thread
    def run_sync():
        with current_app.app_context():
            try:
                service = SyncService(
                    user_id=user_id,
                    discogs_username=discogs_username,
                    oauth_token=oauth_token,
                    oauth_token_secret=oauth_token_secret,
                    personal_token=personal_token,
                )
                service.start_sync(resume=True)
            except DiscogsRateLimitError:
                pass  # Already handled
            except Exception as e:
                progress = SyncProgress.get_latest(user_id=user_id)
                if progress:
                    progress.fail(str(e))
                    db.session.commit()

    thread = threading.Thread(target=run_sync, daemon=True)
    _sync_threads[user_id] = thread
    thread.start()

    return jsonify({"status": "resumed", "message": "Sync resumed"})


@bp.route("/cancel", methods=["POST"])
@login_required
def cancel_sync():
    """Cancel/pause the current sync."""
    latest = SyncProgress.get_latest(user_id=current_user.id)
    if latest and latest.is_running:
        latest.pause()
        db.session.commit()
        return jsonify({"status": "paused", "message": "Sync paused"})

    return jsonify({"error": "No active sync to cancel"}), 400


@bp.route("/history")
@login_required
def sync_history():
    """Get sync history for current user."""
    history = (
        SyncProgress.query
        .filter_by(user_id=current_user.id)
        .order_by(SyncProgress.created_at.desc())
        .limit(10)
        .all()
    )

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
