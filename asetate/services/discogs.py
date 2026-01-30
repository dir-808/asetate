"""Discogs API client with rate limiting and error handling."""

import time
from dataclasses import dataclass
from typing import Iterator

import requests
from flask import current_app
from requests_oauthlib import OAuth1


class DiscogsError(Exception):
    """Base exception for Discogs API errors."""

    pass


class DiscogsRateLimitError(DiscogsError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")


class DiscogsAuthError(DiscogsError):
    """Raised when authentication fails."""

    pass


@dataclass
class DiscogsRelease:
    """A release from the Discogs API."""

    discogs_id: int
    title: str
    artist: str
    label: str | None
    year: int | None
    cover_art_url: str | None
    discogs_uri: str
    tracks: list[dict]


class DiscogsClient:
    """Client for interacting with the Discogs API.

    Handles OAuth 1.0a authentication, rate limiting (60 req/min), and pagination.
    """

    BASE_URL = "https://api.discogs.com"
    USER_AGENT = "Asetate/0.1.0 +https://github.com/asetate/asetate"

    def __init__(
        self,
        oauth_token: str | None = None,
        oauth_token_secret: str | None = None,
    ):
        """Initialize the client with OAuth 1.0a credentials.

        Args:
            oauth_token: Discogs OAuth access token
            oauth_token_secret: Discogs OAuth access token secret
        """
        consumer_key = current_app.config.get("DISCOGS_CONSUMER_KEY")
        consumer_secret = current_app.config.get("DISCOGS_CONSUMER_SECRET")

        if not oauth_token or not oauth_token_secret:
            raise DiscogsAuthError("No Discogs OAuth credentials provided")

        if not consumer_key or not consumer_secret:
            raise DiscogsAuthError("Discogs OAuth not configured on server")

        # Create OAuth1 authentication
        self.auth = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
        )

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

        # Rate limiting state
        self._last_request_time = 0.0
        self._min_request_interval = 1.0  # 1 second between requests (safe margin)

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make a rate-limited request to the Discogs API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/users/{username}/collection")
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response as dict

        Raises:
            DiscogsRateLimitError: If rate limit exceeded
            DiscogsAuthError: If authentication fails
            DiscogsError: For other API errors
        """
        self._rate_limit()

        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, auth=self.auth, **kwargs)

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise DiscogsRateLimitError(retry_after)

        # Handle auth errors
        if response.status_code == 401:
            raise DiscogsAuthError("Invalid or expired token")

        if response.status_code == 403:
            raise DiscogsAuthError("Access forbidden - check token permissions")

        # Handle other errors
        if not response.ok:
            raise DiscogsError(f"API error {response.status_code}: {response.text}")

        return response.json()

    def get_identity(self) -> dict:
        """Get the authenticated user's identity.

        Returns:
            User info including username
        """
        return self._request("GET", "/oauth/identity")

    def get_username(self) -> str:
        """Get the authenticated user's username."""
        identity = self.get_identity()
        return identity["username"]

    def get_collection_folders(self, username: str) -> list[dict]:
        """Get all collection folders for a user.

        Args:
            username: Discogs username

        Returns:
            List of folder objects
        """
        response = self._request("GET", f"/users/{username}/collection/folders")
        return response.get("folders", [])

    def get_collection_page(
        self, username: str, folder_id: int = 0, page: int = 1, per_page: int = 100
    ) -> dict:
        """Get a single page of collection releases.

        Args:
            username: Discogs username
            folder_id: Folder ID (0 = all releases)
            page: Page number (1-indexed)
            per_page: Results per page (max 100)

        Returns:
            Response with releases and pagination info
        """
        return self._request(
            "GET",
            f"/users/{username}/collection/folders/{folder_id}/releases",
            params={"page": page, "per_page": per_page, "sort": "added", "sort_order": "desc"},
        )

    def iter_collection(
        self, username: str, folder_id: int = 0, per_page: int = 100, start_page: int = 1
    ) -> Iterator[tuple[dict, int, int]]:
        """Iterate through all releases in a collection.

        Yields releases one at a time with pagination info for progress tracking.

        Args:
            username: Discogs username
            folder_id: Folder ID (0 = all releases)
            per_page: Results per page
            start_page: Page to start from (for resuming)

        Yields:
            Tuple of (release_data, current_count, total_count)
        """
        page = start_page
        total_count = None
        processed = (start_page - 1) * per_page

        while True:
            response = self.get_collection_page(username, folder_id, page, per_page)
            pagination = response.get("pagination", {})

            if total_count is None:
                total_count = pagination.get("items", 0)

            releases = response.get("releases", [])
            if not releases:
                break

            for release in releases:
                processed += 1
                yield release, processed, total_count

            # Check if there are more pages
            if page >= pagination.get("pages", 1):
                break

            page += 1

    def get_release_details(self, release_id: int) -> dict:
        """Get detailed info for a specific release including tracklist.

        Args:
            release_id: Discogs release ID

        Returns:
            Full release data including tracklist
        """
        return self._request("GET", f"/releases/{release_id}")

    def parse_release(self, collection_item: dict, details: dict | None = None) -> DiscogsRelease:
        """Parse a collection item (and optional details) into a DiscogsRelease.

        Args:
            collection_item: Release data from collection endpoint
            details: Optional detailed release data (includes tracklist)

        Returns:
            Parsed DiscogsRelease object
        """
        basic_info = collection_item.get("basic_information", {})

        # Extract artist names
        artists = basic_info.get("artists", [])
        artist_name = ", ".join(a.get("name", "") for a in artists) if artists else "Unknown"
        # Clean up Discogs artist numbering like "Artist (2)"
        artist_name = self._clean_artist_name(artist_name)

        # Extract label
        labels = basic_info.get("labels", [])
        label = labels[0].get("name") if labels else None

        # Extract cover art (prefer larger images)
        cover_url = None
        if basic_info.get("cover_image"):
            cover_url = basic_info["cover_image"]

        # Parse tracks from details if available
        tracks = []
        if details:
            for track in details.get("tracklist", []):
                # Skip headings and index tracks
                if track.get("type_") in ("heading", "index"):
                    continue
                tracks.append(
                    {
                        "position": track.get("position", ""),
                        "title": track.get("title", "Untitled"),
                        "duration": track.get("duration", ""),
                    }
                )

        return DiscogsRelease(
            discogs_id=basic_info.get("id"),
            title=basic_info.get("title", "Untitled"),
            artist=artist_name,
            label=label,
            year=basic_info.get("year") or None,
            cover_art_url=cover_url,
            discogs_uri=f"https://www.discogs.com/release/{basic_info.get('id')}",
            tracks=tracks,
        )

    def _clean_artist_name(self, name: str) -> str:
        """Remove Discogs disambiguation numbers from artist names.

        Discogs uses "(2)", "(3)" etc. to disambiguate artists with the same name.
        """
        import re

        return re.sub(r"\s*\(\d+\)$", "", name)
