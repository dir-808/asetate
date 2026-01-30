"""Authentication routes - Google OAuth and Discogs OAuth 1.0a."""

from datetime import datetime
from urllib.parse import urlencode

from flask import Blueprint, redirect, url_for, request, current_app, session, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth1Session
import requests

from asetate import db, limiter
from asetate.models import User

bp = Blueprint("auth", __name__)

# OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Discogs OAuth 1.0a endpoints
DISCOGS_REQUEST_TOKEN_URL = "https://api.discogs.com/oauth/request_token"
DISCOGS_AUTHORIZE_URL = "https://www.discogs.com/oauth/authorize"
DISCOGS_ACCESS_TOKEN_URL = "https://api.discogs.com/oauth/access_token"
DISCOGS_IDENTITY_URL = "https://api.discogs.com/oauth/identity"


def get_google_provider_cfg():
    """Get Google's OpenID configuration."""
    return requests.get(GOOGLE_DISCOVERY_URL, timeout=10).json()


# =============================================================================
# Google OAuth Routes
# =============================================================================


@bp.route("/login")
@limiter.limit("10 per minute")
def login():
    """Redirect to Google OAuth."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    # Get Google's authorization endpoint
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Build the request URI
    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = url_for("auth.callback", _external=True)

    request_uri = (
        f"{authorization_endpoint}?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile&"
        f"response_type=code"
    )

    return redirect(request_uri)


@bp.route("/callback")
@limiter.limit("10 per minute")
def callback():
    """Handle Google OAuth callback."""
    # Get authorization code from Google
    code = request.args.get("code")
    if not code:
        flash("Login failed - no authorization code received", "error")
        return redirect(url_for("main.index"))

    # Get Google's token endpoint
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Exchange code for tokens
    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]
    redirect_uri = url_for("auth.callback", _external=True)

    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )

    tokens = token_response.json()

    if "error" in tokens:
        flash(f"Login failed: {tokens.get('error_description', 'Unknown error')}", "error")
        return redirect(url_for("main.index"))

    # Get user info from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        timeout=10,
    )

    userinfo = userinfo_response.json()

    if not userinfo.get("email_verified"):
        flash("Email not verified by Google", "error")
        return redirect(url_for("main.index"))

    # Find or create user
    google_id = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo.get("name", "")
    picture = userinfo.get("picture", "")

    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        # Create new user
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Connect your Discogs account to sync your collection.", "success")
    else:
        # Update user info
        user.name = name
        user.picture = picture
        user.last_login = datetime.utcnow()
        db.session.commit()

    # Log the user in
    login_user(user)

    # Redirect to settings if no Discogs credentials
    if not user.has_discogs_credentials:
        return redirect(url_for("auth.settings"))

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
    return render_template("auth/settings.html")


# =============================================================================
# Discogs OAuth 1.0a Routes
# =============================================================================


@bp.route("/connect/discogs")
@login_required
@limiter.limit("10 per minute")
def connect_discogs():
    """Start Discogs OAuth 1.0a flow."""
    consumer_key = current_app.config["DISCOGS_CONSUMER_KEY"]
    consumer_secret = current_app.config["DISCOGS_CONSUMER_SECRET"]

    if not consumer_key or not consumer_secret:
        flash("Discogs OAuth not configured. Please contact the administrator.", "error")
        return redirect(url_for("auth.settings"))

    # Create OAuth1 session for request token
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        callback_uri=url_for("auth.discogs_callback", _external=True),
    )

    try:
        # Get request token
        response = oauth.fetch_request_token(
            DISCOGS_REQUEST_TOKEN_URL,
            headers={"User-Agent": "Asetate/0.1 +https://github.com/asetate/asetate"},
        )
    except Exception as e:
        current_app.logger.error(f"Discogs OAuth error: {e}")
        flash("Failed to connect to Discogs. Please try again.", "error")
        return redirect(url_for("auth.settings"))

    # Store request token in session for callback
    session["discogs_oauth_token"] = response["oauth_token"]
    session["discogs_oauth_token_secret"] = response["oauth_token_secret"]

    # Redirect user to Discogs for authorization
    authorization_url = f"{DISCOGS_AUTHORIZE_URL}?oauth_token={response['oauth_token']}"
    return redirect(authorization_url)


@bp.route("/connect/discogs/callback")
@login_required
@limiter.limit("10 per minute")
def discogs_callback():
    """Handle Discogs OAuth 1.0a callback."""
    # Check for denied authorization
    if request.args.get("denied"):
        flash("Discogs authorization was denied.", "error")
        return redirect(url_for("auth.settings"))

    # Get verifier from callback
    oauth_verifier = request.args.get("oauth_verifier")
    if not oauth_verifier:
        flash("Invalid callback from Discogs.", "error")
        return redirect(url_for("auth.settings"))

    # Retrieve request token from session
    oauth_token = session.pop("discogs_oauth_token", None)
    oauth_token_secret = session.pop("discogs_oauth_token_secret", None)

    if not oauth_token or not oauth_token_secret:
        flash("OAuth session expired. Please try again.", "error")
        return redirect(url_for("auth.settings"))

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
            headers={"User-Agent": "Asetate/0.1 +https://github.com/asetate/asetate"},
        )
    except Exception as e:
        current_app.logger.error(f"Discogs access token error: {e}")
        flash("Failed to complete Discogs authorization. Please try again.", "error")
        return redirect(url_for("auth.settings"))

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
            headers={"User-Agent": "Asetate/0.1 +https://github.com/asetate/asetate"},
        )
        identity_response.raise_for_status()
        identity = identity_response.json()
    except Exception as e:
        current_app.logger.error(f"Discogs identity error: {e}")
        flash("Failed to verify Discogs identity. Please try again.", "error")
        return redirect(url_for("auth.settings"))

    # Save credentials
    username = identity.get("username")
    if not username:
        flash("Could not get Discogs username.", "error")
        return redirect(url_for("auth.settings"))

    current_user.update_discogs_credentials(username, access_token, access_token_secret)
    db.session.commit()

    flash(f"Successfully connected to Discogs as {username}!", "success")
    return redirect(url_for("auth.settings"))


@bp.route("/disconnect/discogs", methods=["POST"])
@login_required
def disconnect_discogs():
    """Disconnect Discogs account."""
    current_user.clear_discogs_credentials()
    db.session.commit()

    flash("Discogs account disconnected.", "info")
    return redirect(url_for("auth.settings"))
