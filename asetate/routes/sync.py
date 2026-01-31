"""Sync routes - Discogs collection synchronization."""

import threading

from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required, current_user

from asetate import db, limiter
from asetate.services import (
    SyncService,
    get_sync_status,
    DiscogsAuthError,
    DiscogsRateLimitError,
    create_auto_backup,
    InventorySyncService,
    get_inventory_sync_status,
    get_inventory_notifications,
)
from asetate.models import SyncProgress, Release, InventoryListing
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

    # Capture the actual app object (not the proxy) for use in background thread
    app = current_app._get_current_object()

    # Start sync in background thread
    def run_sync():
        with app.app_context():
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

    # Capture the actual app object (not the proxy) for use in background thread
    app = current_app._get_current_object()

    # Start sync in background thread
    def run_sync():
        with app.app_context():
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


# =============================================================================
# Inventory Sync Routes
# =============================================================================

# Track running inventory syncs
_inventory_sync_threads: dict[int, threading.Thread] = {}
_inventory_sync_status: dict[int, dict] = {}


@bp.route("/inventory/status")
@login_required
def inventory_status_api():
    """Get current inventory sync status as JSON."""
    user_id = current_user.id

    # Check if sync is running
    is_running = user_id in _inventory_sync_threads and _inventory_sync_threads[user_id].is_alive()

    # Get stored status from last sync
    stored_status = get_inventory_sync_status(user_id)

    # Get in-progress status if running
    progress_status = _inventory_sync_status.get(user_id, {})

    return jsonify({
        "is_running": is_running,
        "items_synced": stored_status["items_synced"],
        "last_sync": stored_status["last_sync"],
        **progress_status,
    })


@bp.route("/inventory/start", methods=["POST"])
@login_required
@limiter.limit("5 per hour")
def start_inventory_sync():
    """Start a full inventory sync.

    Fetches all inventory listings from Discogs and updates matching releases.
    """
    user_id = current_user.id

    # Check if already syncing
    if user_id in _inventory_sync_threads and _inventory_sync_threads[user_id].is_alive():
        return jsonify({"error": "Inventory sync already in progress"}), 409

    # Check for valid credentials
    if not current_user.has_discogs_credentials:
        return jsonify({"error": "Discogs credentials not configured"}), 400

    # Check if user has seller mode enabled
    if not current_user.is_seller_mode:
        return jsonify({"error": "Seller mode must be enabled to sync inventory"}), 400

    # Capture credentials for background thread
    discogs_username = current_user.discogs_username
    oauth_token = current_user.oauth_token
    oauth_token_secret = current_user.oauth_token_secret
    personal_token = current_user.personal_token

    # Clear previous status
    _inventory_sync_status[user_id] = {"status": "running", "message": "Starting inventory sync..."}

    # Capture the actual app object (not the proxy) for use in background thread
    app = current_app._get_current_object()

    def run_inventory_sync():
        with app.app_context():
            try:
                _inventory_sync_status[user_id] = {
                    "status": "running",
                    "message": "Fetching inventory from Discogs...",
                }

                service = InventorySyncService(
                    user_id=user_id,
                    discogs_username=discogs_username,
                    oauth_token=oauth_token,
                    oauth_token_secret=oauth_token_secret,
                    personal_token=personal_token,
                )

                stats = service.sync_full_inventory()

                # Build completion message
                msg_parts = []
                if stats["created"]:
                    msg_parts.append(f"{stats['created']} new")
                if stats["updated"]:
                    msg_parts.append(f"{stats['updated']} updated")
                if stats["sold"]:
                    msg_parts.append(f"{stats['sold']} sold")

                message = f"Synced {stats['total_listings']} listings"
                if msg_parts:
                    message += f" ({', '.join(msg_parts)})"

                _inventory_sync_status[user_id] = {
                    "status": "completed",
                    "message": message,
                    "stats": stats,
                }

            except DiscogsAuthError as e:
                _inventory_sync_status[user_id] = {
                    "status": "failed",
                    "message": f"Authentication failed: {e}",
                }
            except DiscogsRateLimitError as e:
                _inventory_sync_status[user_id] = {
                    "status": "failed",
                    "message": f"Rate limited. Please wait {e.retry_after}s and try again.",
                }
            except Exception as e:
                app.logger.error(f"Inventory sync error: {e}")
                _inventory_sync_status[user_id] = {
                    "status": "failed",
                    "message": f"Error: {str(e)}",
                }

    thread = threading.Thread(target=run_inventory_sync, daemon=True)
    _inventory_sync_threads[user_id] = thread
    thread.start()

    return jsonify({"status": "started", "message": "Inventory sync started"})


@bp.route("/inventory/release/<int:release_id>", methods=["POST"])
@login_required
@limiter.limit("30 per minute")
def sync_release_inventory(release_id: int):
    """Sync inventory data for a single release.

    This allows ad-hoc syncing of individual releases rather than full sync.
    Useful when a user has just listed or updated an item on Discogs.
    """
    user_id = current_user.id

    # Check for valid credentials
    if not current_user.has_discogs_credentials:
        return jsonify({"error": "Discogs credentials not configured"}), 400

    # Check if user has seller mode enabled
    if not current_user.is_seller_mode:
        return jsonify({"error": "Seller mode must be enabled to sync inventory"}), 400

    # Verify release belongs to user
    release = Release.query.filter_by(id=release_id, user_id=user_id).first()
    if not release:
        return jsonify({"error": "Release not found"}), 404

    try:
        service = InventorySyncService.from_user(current_user)
        result = service.sync_single_release(release_id)

        if result["success"]:
            if result.get("found"):
                return jsonify({
                    "status": "synced",
                    "message": f"Found listing: {result['condition']} - {result['price']}",
                    "condition": result.get("condition"),
                    "price": result.get("price"),
                })
            else:
                return jsonify({
                    "status": "not_listed",
                    "message": result.get("message", "Item not found in inventory"),
                })
        else:
            return jsonify({"error": result.get("error", "Sync failed")}), 400

    except DiscogsAuthError as e:
        return jsonify({"error": f"Authentication failed: {e}"}), 401
    except DiscogsRateLimitError as e:
        return jsonify({"error": f"Rate limited. Retry after {e.retry_after}s"}), 429
    except Exception as e:
        current_app.logger.error(f"Release inventory sync error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# Inventory Notification Routes
# =============================================================================


@bp.route("/inventory/notifications")
@login_required
def inventory_notifications():
    """Get inventory notifications (sold/removed items)."""
    if not current_user.is_seller_mode:
        return jsonify({"notifications": []})

    notifications = get_inventory_notifications(current_user.id)
    return jsonify({"notifications": notifications})


@bp.route("/inventory/notifications/<int:listing_id>/dismiss", methods=["POST"])
@login_required
def dismiss_inventory_notification(listing_id: int):
    """Dismiss a sold/removed notification."""
    listing = InventoryListing.query.filter_by(
        id=listing_id,
        user_id=current_user.id,
    ).first()

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    listing.dismiss_notification()
    db.session.commit()

    return jsonify({"status": "dismissed"})


@bp.route("/inventory/notifications/dismiss-all", methods=["POST"])
@login_required
def dismiss_all_inventory_notifications():
    """Dismiss all sold/removed notifications."""
    from asetate.models.inventory_listing import ListingStatus

    InventoryListing.query.filter(
        InventoryListing.user_id == current_user.id,
        InventoryListing.status.in_([ListingStatus.SOLD, ListingStatus.REMOVED]),
        InventoryListing.notification_dismissed == False,
    ).update({"notification_dismissed": True}, synchronize_session=False)

    db.session.commit()

    return jsonify({"status": "all_dismissed"})
