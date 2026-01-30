"""Authentication routes - supports both OAuth and Personal Access Token modes."""

import json
from datetime import datetime

from flask import Blueprint, redirect, url_for, request, current_app, session, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth1Session

from asetate import db, limiter
from asetate.models import User

bp = Blueprint("auth", __name__)

# Discogs OAuth 1.0a endpoints
DISCOGS_REQUEST_TOKEN_URL = "https://api.discogs.com/oauth/request_token"
DISCOGS_AUTHORIZE_URL = "https://www.discogs.com/oauth/authorize"
DISCOGS_ACCESS_TOKEN_URL = "https://api.discogs.com/oauth/access_token"
DISCOGS_IDENTITY_URL = "https://api.discogs.com/oauth/identity"

USER_AGENT = "Asetate/0.1 +https://github.com/asetate/asetate"


def is_oauth_mode() -> bool:
    """Check if the app is configured for OAuth mode (hosted) or PAT mode (self-hosted)."""
    consumer_key = current_app.config.get("DISCOGS_CONSUMER_KEY")
    consumer_secret = current_app.config.get("DISCOGS_CONSUMER_SECRET")
    return bool(consumer_key and consumer_secret)


def get_or_create_local_user() -> User:
    """Get or create the local user for PAT mode (single-user self-hosted)."""
    user = User.query.first()
    if not user:
        user = User(discogs_username="local_user")
        db.session.add(user)
        db.session.commit()
    return user


# =============================================================================
# Mode-aware login
# =============================================================================


@bp.route("/login")
@limiter.limit("10 per minute")
def login():
    """Start login flow - OAuth or auto-login for PAT mode."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if is_oauth_mode():
        # OAuth mode: redirect to Discogs
        return _oauth_login()
    else:
        # PAT mode: auto-login as local user, redirect to settings to configure
        user = get_or_create_local_user()
        login_user(user)
        if not user.has_discogs_credentials:
            flash("Welcome! Please configure your Discogs credentials to get started.", "info")
            return redirect(url_for("auth.settings"))
        return redirect(url_for("main.index"))


def _oauth_login():
    """Start Discogs OAuth 1.0a login flow."""
    consumer_key = current_app.config.get("DISCOGS_CONSUMER_KEY")
    consumer_secret = current_app.config.get("DISCOGS_CONSUMER_SECRET")

    # Create OAuth1 session for request token
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        callback_uri=url_for("auth.callback", _external=True),
    )

    try:
        # Get request token
        response = oauth.fetch_request_token(
            DISCOGS_REQUEST_TOKEN_URL,
            headers={"User-Agent": USER_AGENT},
        )
    except Exception as e:
        current_app.logger.error(f"Discogs OAuth error: {e}")
        flash("Failed to connect to Discogs. Please try again.", "error")
        return redirect(url_for("main.index"))

    # Store request token in session for callback
    session["discogs_oauth_token"] = response["oauth_token"]
    session["discogs_oauth_token_secret"] = response["oauth_token_secret"]

    # Redirect user to Discogs for authorization
    authorization_url = f"{DISCOGS_AUTHORIZE_URL}?oauth_token={response['oauth_token']}"
    return redirect(authorization_url)


@bp.route("/callback")
@limiter.limit("10 per minute")
def callback():
    """Handle Discogs OAuth 1.0a callback and log user in."""
    if not is_oauth_mode():
        return redirect(url_for("main.index"))

    # Check for denied authorization
    if request.args.get("denied"):
        flash("Discogs authorization was denied.", "error")
        return redirect(url_for("main.index"))

    # Get verifier from callback
    oauth_verifier = request.args.get("oauth_verifier")
    if not oauth_verifier:
        flash("Invalid callback from Discogs.", "error")
        return redirect(url_for("main.index"))

    # Retrieve request token from session
    oauth_token = session.pop("discogs_oauth_token", None)
    oauth_token_secret = session.pop("discogs_oauth_token_secret", None)

    if not oauth_token or not oauth_token_secret:
        flash("Login session expired. Please try again.", "error")
        return redirect(url_for("main.index"))

    consumer_key = current_app.config["DISCOGS_CONSUMER_KEY"]
    consumer_secret = current_app.config["DISCOGS_CONSUMER_SECRET"]

    # Create OAuth1 session for access token exchange
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
        verifier=oauth_verifier,
    )

    try:
        # Exchange request token for access token
        tokens = oauth.fetch_access_token(
            DISCOGS_ACCESS_TOKEN_URL,
            headers={"User-Agent": USER_AGENT},
        )
    except Exception as e:
        current_app.logger.error(f"Discogs access token error: {e}")
        flash("Failed to complete Discogs login. Please try again.", "error")
        return redirect(url_for("main.index"))

    access_token = tokens["oauth_token"]
    access_token_secret = tokens["oauth_token_secret"]

    # Get user identity from Discogs
    identity_oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    try:
        identity_response = identity_oauth.get(
            DISCOGS_IDENTITY_URL,
            headers={"User-Agent": USER_AGENT},
        )
        identity_response.raise_for_status()
        identity = identity_response.json()
    except Exception as e:
        current_app.logger.error(f"Discogs identity error: {e}")
        flash("Failed to verify Discogs identity. Please try again.", "error")
        return redirect(url_for("main.index"))

    # Extract identity info
    discogs_id = identity.get("id")
    username = identity.get("username")

    if not discogs_id or not username:
        flash("Could not get Discogs identity.", "error")
        return redirect(url_for("main.index"))

    # Find or create user
    user = User.query.filter_by(discogs_id=discogs_id).first()

    if not user:
        # Create new user
        user = User(
            discogs_id=discogs_id,
            discogs_username=username,
        )
        db.session.add(user)
        flash(f"Welcome to Asetate, {username}! Your account has been created.", "success")
    else:
        # Update user info
        user.discogs_username = username  # In case it changed
        user.last_login = datetime.utcnow()

    # Always update tokens (they may have changed)
    user.update_oauth_tokens(access_token, access_token_secret)
    db.session.commit()

    # Log the user in
    login_user(user)

    return redirect(url_for("main.index"))


@bp.route("/logout")
@login_required
def logout():
    """Log out the user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# =============================================================================
# Settings
# =============================================================================


@bp.route("/settings")
@login_required
def settings():
    """User settings page."""
    return render_template(
        "auth/settings.html",
        oauth_mode=is_oauth_mode(),
    )


@bp.route("/settings/token", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def save_token():
    """Save Personal Access Token (PAT mode only)."""
    if is_oauth_mode():
        flash("Cannot set token in OAuth mode.", "error")
        return redirect(url_for("auth.settings"))

    username = request.form.get("username", "").strip()
    token = request.form.get("token", "").strip()

    if not username or not token:
        flash("Please provide both username and token.", "error")
        return redirect(url_for("auth.settings"))

    # Validate the token by trying to access the collection
    from asetate.services.discogs import DiscogsClient, DiscogsAuthError

    try:
        client = DiscogsClient(personal_token=token)
        if not client.verify_token(username):
            flash("Invalid token or username. Please check your credentials.", "error")
            return redirect(url_for("auth.settings"))
    except DiscogsAuthError as e:
        flash(f"Authentication failed: {e}", "error")
        return redirect(url_for("auth.settings"))
    except Exception as e:
        current_app.logger.error(f"Token validation error: {e}")
        flash("Failed to validate token. Please try again.", "error")
        return redirect(url_for("auth.settings"))

    # Save the token
    current_user.update_personal_token(username, token)
    db.session.commit()

    flash(f"Successfully connected to Discogs as {username}!", "success")
    return redirect(url_for("auth.settings"))


# =============================================================================
# Backup / Export / Import
# =============================================================================


@bp.route("/settings/export")
@login_required
def export_data():
    """Export all user data as JSON download."""
    from flask import Response
    from asetate.services import BackupService

    service = BackupService(current_user.id)
    json_data = service.export_to_json(pretty=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"asetate_backup_{timestamp}.json"

    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@bp.route("/settings/import", methods=["POST"])
@login_required
@limiter.limit("5 per hour")
def import_data():
    """Import user data from uploaded JSON file."""
    from asetate.services import BackupService

    if "file" not in request.files:
        flash("No file uploaded.", "error")
        return redirect(url_for("auth.settings"))

    file = request.files["file"]
    if not file.filename:
        flash("No file selected.", "error")
        return redirect(url_for("auth.settings"))

    if not file.filename.endswith(".json"):
        flash("Please upload a JSON file.", "error")
        return redirect(url_for("auth.settings"))

    try:
        json_data = file.read().decode("utf-8")
        service = BackupService(current_user.id)
        stats = service.import_from_json(json_data)

        flash(
            f"Import complete! Tags: {stats['tags_created']}, "
            f"Tracks updated: {stats['tracks_updated']}, "
            f"Crates: {stats['crates_created']}",
            "success",
        )
    except json.JSONDecodeError:
        flash("Invalid JSON file.", "error")
    except ValueError as e:
        flash(f"Import error: {e}", "error")
    except Exception as e:
        current_app.logger.error(f"Import error: {e}")
        flash("Failed to import data. Please check the file format.", "error")

    return redirect(url_for("auth.settings"))
