#!/usr/bin/env python3
"""Seed the database with demo data for preview deployments.

This script creates realistic sample data to demonstrate Asetate's features
without requiring a Discogs account or API connection.

Only runs if the database is empty (no users exist).
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from asetate import create_app, db
from asetate.models import User, Release, Track, Crate, Tag


def create_demo_user():
    """Create a demo user (no real credentials)."""
    user = User(
        discogs_username="demo_dj",
        preferences={
            "seller_mode": False,
            "key_notation": "camelot",
            "visible_track_fields": [
                "position",
                "title",
                "duration",
                "bpm",
                "key",
                "energy",
                "tags",
                "playable",
            ],
        },
    )
    db.session.add(user)
    db.session.flush()  # Get user.id
    return user


def create_demo_releases(user):
    """Create demo releases with realistic DJ vinyl data."""

    releases_data = [
        {
            "discogs_id": 1001,
            "title": "Selected Ambient Works 85-92",
            "artist": "Aphex Twin",
            "label": "R&S Records",
            "year": 1992,
            "country": "Belgium",
            "format_details": "2xLP, Album, RE",
            "catno": "AMB LP 3922",
            "genres": ["Electronic"],
            "styles": ["Ambient", "Techno", "IDM"],
            "cover_art_url": "https://i.discogs.com/placeholder-ambient.jpg",
            "notes": "Essential ambient album. Side A perfect for warm-up sets.",
            "tracks": [
                {"position": "A1", "title": "Xtal", "duration": "4:54", "bpm": 100, "key": "8A", "energy": 2, "playable": True},
                {"position": "A2", "title": "Tha", "duration": "9:01", "bpm": 92, "key": "5A", "energy": 2, "playable": True},
                {"position": "B1", "title": "Pulsewidth", "duration": "3:47", "bpm": 130, "key": "11A", "energy": 3, "playable": True},
                {"position": "B2", "title": "Ageispolis", "duration": "5:23", "bpm": 101, "key": "4A", "energy": 2, "playable": True},
                {"position": "C1", "title": "Green Calx", "duration": "6:03", "bpm": 84, "key": "9A", "energy": 2, "playable": False},
                {"position": "C2", "title": "Heliosphan", "duration": "4:52", "bpm": 115, "key": "6A", "energy": 3, "playable": True},
            ],
        },
        {
            "discogs_id": 1002,
            "title": "Music Has The Right To Children",
            "artist": "Boards Of Canada",
            "label": "Warp Records",
            "year": 1998,
            "country": "UK",
            "format_details": "2xLP, Album",
            "catno": "WARP LP55",
            "genres": ["Electronic"],
            "styles": ["IDM", "Ambient", "Downtempo"],
            "cover_art_url": "https://i.discogs.com/placeholder-boc.jpg",
            "tracks": [
                {"position": "A1", "title": "Wildlife Analysis", "duration": "0:46", "bpm": None, "key": None, "energy": 1, "playable": False},
                {"position": "A2", "title": "An Eagle In Your Mind", "duration": "6:24", "bpm": 104, "key": "4B", "energy": 3, "playable": True},
                {"position": "A3", "title": "Telephasic Workshop", "duration": "6:35", "bpm": 101, "key": "8A", "energy": 3, "playable": True},
                {"position": "B1", "title": "Turquoise Hexagon Sun", "duration": "5:07", "bpm": 91, "key": "6A", "energy": 2, "playable": True},
                {"position": "B2", "title": "Kaini Industries", "duration": "0:58", "bpm": None, "key": None, "energy": 1, "playable": False},
                {"position": "B3", "title": "Bocuma", "duration": "2:40", "bpm": 105, "key": "11B", "energy": 2, "playable": True},
            ],
        },
        {
            "discogs_id": 1003,
            "title": "Untrue",
            "artist": "Burial",
            "label": "Hyperdub",
            "year": 2007,
            "country": "UK",
            "format_details": "2xLP, Album",
            "catno": "HDBLP002",
            "genres": ["Electronic"],
            "styles": ["Dubstep", "Future Garage", "UK Garage"],
            "cover_art_url": "https://i.discogs.com/placeholder-burial.jpg",
            "notes": "Late night essential. Archangel is the standout.",
            "tracks": [
                {"position": "A1", "title": "Untitled", "duration": "1:15", "bpm": None, "key": None, "energy": 1, "playable": False},
                {"position": "A2", "title": "Archangel", "duration": "4:00", "bpm": 130, "key": "1A", "energy": 4, "playable": True, "notes": "Peak time track - huge vocal chop"},
                {"position": "A3", "title": "Near Dark", "duration": "4:48", "bpm": 130, "key": "6A", "energy": 3, "playable": True},
                {"position": "B1", "title": "Ghost Hardware", "duration": "4:55", "bpm": 130, "key": "8A", "energy": 4, "playable": True},
                {"position": "B2", "title": "Endorphin", "duration": "3:59", "bpm": 130, "key": "3A", "energy": 3, "playable": True},
                {"position": "C1", "title": "Etched Headplate", "duration": "4:38", "bpm": 128, "key": "5A", "energy": 3, "playable": True},
                {"position": "C2", "title": "In McDonalds", "duration": "4:12", "bpm": 130, "key": "11A", "energy": 3, "playable": True},
                {"position": "D1", "title": "Untrue", "duration": "6:29", "bpm": 128, "key": "8A", "energy": 4, "playable": True},
                {"position": "D2", "title": "Shell Of Light", "duration": "5:30", "bpm": 130, "key": "4A", "energy": 3, "playable": True},
            ],
        },
        {
            "discogs_id": 1004,
            "title": "Homework",
            "artist": "Daft Punk",
            "label": "Virgin",
            "year": 1997,
            "country": "France",
            "format_details": "2xLP, Album",
            "catno": "V2821",
            "genres": ["Electronic"],
            "styles": ["House", "Techno", "Electro"],
            "cover_art_url": "https://i.discogs.com/placeholder-daftpunk.jpg",
            "tracks": [
                {"position": "A1", "title": "Daftendirekt", "duration": "2:44", "bpm": 122, "key": "5A", "energy": 3, "playable": True},
                {"position": "A2", "title": "WDPK 83.7 FM", "duration": "0:28", "bpm": None, "key": None, "energy": 1, "playable": False},
                {"position": "A3", "title": "Revolution 909", "duration": "5:26", "bpm": 126, "key": "7A", "energy": 4, "playable": True, "notes": "Classic filter house - crowd pleaser"},
                {"position": "B1", "title": "Da Funk", "duration": "5:28", "bpm": 116, "key": "6A", "energy": 4, "playable": True},
                {"position": "B2", "title": "Phoenix", "duration": "4:55", "bpm": 125, "key": "8B", "energy": 4, "playable": True},
                {"position": "C1", "title": "Fresh", "duration": "4:03", "bpm": 123, "key": "4A", "energy": 3, "playable": True},
                {"position": "C2", "title": "Around The World", "duration": "7:09", "bpm": 121, "key": "6A", "energy": 5, "playable": True, "notes": "Absolute banger - use for peak energy"},
                {"position": "D1", "title": "Rollin' & Scratchin'", "duration": "7:27", "bpm": 130, "key": "9A", "energy": 5, "playable": True},
                {"position": "D2", "title": "Teachers", "duration": "2:52", "bpm": 128, "key": "2A", "energy": 3, "playable": True},
            ],
        },
        {
            "discogs_id": 1005,
            "title": "Endtroducing.....",
            "artist": "DJ Shadow",
            "label": "Mo' Wax",
            "year": 1996,
            "country": "UK",
            "format_details": "2xLP, Album",
            "catno": "MW059LP",
            "genres": ["Electronic", "Hip Hop"],
            "styles": ["Trip Hop", "Abstract", "Downtempo"],
            "cover_art_url": "https://i.discogs.com/placeholder-shadow.jpg",
            "tracks": [
                {"position": "A1", "title": "Best Foot Forward", "duration": "0:32", "bpm": None, "key": None, "energy": 1, "playable": False},
                {"position": "A2", "title": "Building Steam With A Grain Of Salt", "duration": "6:48", "bpm": 89, "key": "5A", "energy": 3, "playable": True},
                {"position": "A3", "title": "The Number Song", "duration": "4:34", "bpm": 98, "key": "9A", "energy": 4, "playable": True},
                {"position": "B1", "title": "Changeling", "duration": "5:06", "bpm": 76, "key": "3A", "energy": 2, "playable": True},
                {"position": "B2", "title": "What Does Your Soul Look Like (Part 1)", "duration": "4:57", "bpm": 85, "key": "6A", "energy": 3, "playable": True},
                {"position": "C1", "title": "Organ Donor", "duration": "4:06", "bpm": 93, "key": "8A", "energy": 4, "playable": True, "notes": "Great for transitions - builds nicely"},
                {"position": "C2", "title": "Stem / Long Stem", "duration": "8:04", "bpm": 83, "key": "1A", "energy": 3, "playable": True},
                {"position": "D1", "title": "Midnight In A Perfect World", "duration": "5:01", "bpm": 78, "key": "4A", "energy": 2, "playable": True},
            ],
        },
        {
            "discogs_id": 1006,
            "title": "Cross",
            "artist": "Justice",
            "label": "Ed Banger Records",
            "year": 2007,
            "country": "France",
            "format_details": "2xLP, Album, Gat",
            "catno": "ED011LP",
            "genres": ["Electronic"],
            "styles": ["Electro House", "French House"],
            "cover_art_url": "https://i.discogs.com/placeholder-justice.jpg",
            "notes": "High energy throughout. Careful with levels - mastered hot.",
            "tracks": [
                {"position": "A1", "title": "Genesis", "duration": "4:04", "bpm": 122, "key": "4A", "energy": 4, "playable": True},
                {"position": "A2", "title": "Let There Be Light", "duration": "4:31", "bpm": 130, "key": "6A", "energy": 4, "playable": True},
                {"position": "A3", "title": "D.A.N.C.E.", "duration": "4:03", "bpm": 122, "key": "5B", "energy": 5, "playable": True, "notes": "Massive crowd reaction guaranteed"},
                {"position": "B1", "title": "Newjack", "duration": "3:30", "bpm": 125, "key": "8A", "energy": 4, "playable": True},
                {"position": "B2", "title": "Phantom", "duration": "4:55", "bpm": 127, "key": "1A", "energy": 5, "playable": True},
                {"position": "B3", "title": "Phantom Pt. II", "duration": "4:50", "bpm": 124, "key": "1A", "energy": 5, "playable": True},
                {"position": "C1", "title": "Valentine", "duration": "4:27", "bpm": 118, "key": "3A", "energy": 3, "playable": True},
                {"position": "C2", "title": "Tthhee Ppaarrttyy", "duration": "4:35", "bpm": 128, "key": "9A", "energy": 4, "playable": True},
                {"position": "D1", "title": "Waters Of Nazareth", "duration": "4:08", "bpm": 130, "key": "6A", "energy": 5, "playable": True},
                {"position": "D2", "title": "Stress", "duration": "4:47", "bpm": 132, "key": "8A", "energy": 5, "playable": True},
            ],
        },
    ]

    releases = []
    all_tracks = []

    for data in releases_data:
        tracks_data = data.pop("tracks")

        release = Release(
            user_id=user.id,
            synced_at=datetime.utcnow() - timedelta(days=30),
            **data,
        )
        db.session.add(release)
        db.session.flush()

        for track_data in tracks_data:
            track = Track(
                release_id=release.id,
                position=track_data.get("position"),
                title=track_data["title"],
                duration=track_data.get("duration"),
                bpm=track_data.get("bpm"),
                camelot=track_data.get("key"),  # Using Camelot notation
                energy=track_data.get("energy"),
                is_playable=track_data.get("playable", False),
                notes=track_data.get("notes"),
            )
            db.session.add(track)
            all_tracks.append(track)

        releases.append(release)

    db.session.flush()
    return releases, all_tracks


def create_demo_crates(user, releases):
    """Create demo crates and assign releases."""

    # Create top-level crates
    crates = {}

    crates["favorites"] = Crate(
        user_id=user.id,
        name="Favorites",
        description="All-time favorites - never leave home without these",
        color="orange",
        icon="emoji:2B50",  # Star
        sort_order=0,
    )

    crates["house"] = Crate(
        user_id=user.id,
        name="House",
        description="French house, filter house, and classics",
        color="blue",
        icon="emoji:1F3E0",  # House
        sort_order=1,
    )

    crates["ambient"] = Crate(
        user_id=user.id,
        name="Ambient / Downtempo",
        description="Warm-up and cool-down selections",
        color="green",
        icon="emoji:1F30A",  # Wave
        sort_order=2,
    )

    crates["peak_time"] = Crate(
        user_id=user.id,
        name="Peak Time",
        description="High energy bangers for the main room",
        color="red",
        icon="emoji:1F525",  # Fire
        sort_order=3,
    )

    crates["uk"] = Crate(
        user_id=user.id,
        name="UK Bass",
        description="Garage, dubstep, and UK sounds",
        color="purple",
        icon="emoji:1F1EC",  # Flag
        sort_order=4,
    )

    for crate in crates.values():
        db.session.add(crate)

    db.session.flush()

    # Assign releases to crates
    # Favorites: best albums
    crates["favorites"].releases.extend([releases[2], releases[3]])  # Burial, Daft Punk

    # House: Daft Punk, Justice
    crates["house"].releases.extend([releases[3], releases[5]])

    # Ambient: Aphex Twin, Boards of Canada, DJ Shadow
    crates["ambient"].releases.extend([releases[0], releases[1], releases[4]])

    # Peak Time: Justice
    crates["peak_time"].releases.append(releases[5])

    # UK Bass: Burial
    crates["uk"].releases.append(releases[2])

    return crates


def create_demo_tags(user, tracks):
    """Create demo tags and assign to tracks."""

    tags_data = [
        {"name": "Vocals", "color": "#9065B0"},  # Purple
        {"name": "Instrumental", "color": "#337EA9"},  # Blue
        {"name": "Build", "color": "#D9730D"},  # Orange
        {"name": "Drop", "color": "#D44C47"},  # Red
        {"name": "Chill", "color": "#448361"},  # Green
        {"name": "Crowd Pleaser", "color": "#CB912F"},  # Yellow
    ]

    tags = {}
    for data in tags_data:
        tag = Tag(user_id=user.id, **data)
        db.session.add(tag)
        tags[data["name"]] = tag

    db.session.flush()

    # Assign tags to some tracks (by title matching)
    tag_assignments = {
        "Archangel": ["Vocals", "Drop", "Crowd Pleaser"],
        "D.A.N.C.E.": ["Vocals", "Crowd Pleaser"],
        "Around The World": ["Vocals", "Crowd Pleaser", "Drop"],
        "Da Funk": ["Instrumental", "Build"],
        "Xtal": ["Chill", "Instrumental"],
        "Turquoise Hexagon Sun": ["Chill", "Instrumental"],
        "Waters Of Nazareth": ["Drop", "Instrumental"],
        "Phantom": ["Build", "Drop"],
        "Organ Donor": ["Build", "Instrumental"],
        "Midnight In A Perfect World": ["Chill", "Instrumental"],
    }

    for track in tracks:
        if track.title in tag_assignments:
            for tag_name in tag_assignments[track.title]:
                if tag_name in tags:
                    track.tags.append(tags[tag_name])

    return tags


def seed_database():
    """Main seeding function."""
    app = create_app(os.environ.get("FLASK_ENV", "production"))

    with app.app_context():
        # Create tables if they don't exist (for fresh deployments)
        db.create_all()

        # Check if data already exists
        existing_users = User.query.count()
        if existing_users > 0:
            print(f"Database already has {existing_users} user(s). Skipping seed.")
            return False

        print("Seeding demo data...")

        # Create demo data
        user = create_demo_user()
        print(f"  Created user: {user.discogs_username}")

        releases, tracks = create_demo_releases(user)
        print(f"  Created {len(releases)} releases with {len(tracks)} tracks")

        crates = create_demo_crates(user, releases)
        print(f"  Created {len(crates)} crates")

        tags = create_demo_tags(user, tracks)
        print(f"  Created {len(tags)} tags")

        # Commit all changes
        db.session.commit()
        print("Demo data seeded successfully!")

        # Print summary
        playable_count = sum(1 for t in tracks if t.is_playable)
        print(f"\nSummary:")
        print(f"  - {len(releases)} releases")
        print(f"  - {len(tracks)} tracks ({playable_count} playable)")
        print(f"  - {len(crates)} crates")
        print(f"  - {len(tags)} tags")
        print(f"\nDemo user: {user.discogs_username} (no password needed)")

        return True


if __name__ == "__main__":
    seed_database()
