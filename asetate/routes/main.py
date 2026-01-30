"""Main routes - home page and general navigation."""

from flask import Blueprint, render_template

from asetate.models import Release, Track, Crate

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page - dashboard overview."""
    # Get collection stats
    total_releases = Release.query.filter(Release.discogs_removed_at.is_(None)).count()
    total_tracks = Track.query.join(Release).filter(Release.discogs_removed_at.is_(None)).count()
    playable_tracks = (
        Track.query.join(Release)
        .filter(Release.discogs_removed_at.is_(None), Track.is_playable == True)
        .count()
    )
    total_crates = Crate.query.count()

    stats = {
        "releases": total_releases,
        "tracks": total_tracks,
        "playable": playable_tracks,
        "crates": total_crates,
    }

    return render_template("index.html", stats=stats)


@bp.route("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
