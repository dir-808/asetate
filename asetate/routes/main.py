"""Main routes - home page and general navigation."""

from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page - dashboard overview."""
    return render_template("index.html")


@bp.route("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
