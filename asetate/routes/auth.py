"""Authentication routes - Google OAuth login."""

import json

from flask import Blueprint, redirect, url_for, request, current_app, session, flash
from flask_login import login_user, logout_user, login_required, current_user
import requests

from asetate import db
from asetate.models import User

bp = Blueprint("auth", __name__)

# Google OAuth endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def get_google_provider_cfg():
    """Get Google's OpenID configuration."""
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@bp.route("/login")
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
        flash("Account created! Add your Discogs credentials to sync your collection.", "success")
    else:
        # Update user info
        user.name = name
        user.picture = picture
        from datetime import datetime
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


@bp.route("/settings")
@login_required
def settings():
    """User settings page."""
    from flask import render_template
    return render_template("auth/settings.html")


@bp.route("/settings/discogs", methods=["POST"])
@login_required
def update_discogs():
    """Update Discogs credentials."""
    data = request.get_json()

    if not data:
        return {"error": "No data provided"}, 400

    username = data.get("username", "").strip()
    token = data.get("token", "").strip()

    if not username or not token:
        return {"error": "Username and token are required"}, 400

    # Verify credentials with Discogs
    try:
        response = requests.get(
            f"https://api.discogs.com/users/{username}",
            headers={
                "Authorization": f"Discogs token={token}",
                "User-Agent": "Asetate/0.1",
            },
        )

        if response.status_code != 200:
            return {"error": "Invalid Discogs credentials"}, 400

    except requests.RequestException:
        return {"error": "Could not verify credentials"}, 500

    # Save credentials
    current_user.update_discogs_credentials(username, token)
    db.session.commit()

    return {"status": "ok", "message": "Discogs credentials updated"}


@bp.route("/settings/discogs", methods=["DELETE"])
@login_required
def remove_discogs():
    """Remove Discogs credentials."""
    current_user.discogs_username = None
    current_user.discogs_token = None
    db.session.commit()

    return {"status": "ok", "message": "Discogs credentials removed"}
