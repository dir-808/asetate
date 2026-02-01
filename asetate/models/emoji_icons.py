"""OpenMoji emoji icons for crate icons.

Loads emoji metadata from openmoji.json and provides search functionality.
SVGs are outline-style and support CSS color styling.

Setup: Run scripts/download-emoji.sh to download emoji SVGs and metadata.
"""

import json
from functools import lru_cache
from pathlib import Path

# Paths
EMOJI_DIR = Path(__file__).parent.parent / "static" / "emoji"
METADATA_FILE = EMOJI_DIR / "openmoji.json"

# Default emoji (folder)
DEFAULT_EMOJI = "1F4C1"  # Open file folder emoji

# Common search aliases to improve discoverability
SEARCH_ALIASES = {
    "music": ["musical", "note", "song", "audio", "sound"],
    "folder": ["file", "directory", "document"],
    "heart": ["love", "like", "favorite"],
    "fire": ["hot", "flame", "burn", "lit"],
    "star": ["favorite", "rating", "best"],
    "party": ["celebration", "birthday", "confetti"],
    "cool": ["sunglasses", "awesome"],
    "sad": ["cry", "unhappy", "disappointed"],
    "happy": ["smile", "joy", "glad"],
    "angry": ["mad", "rage", "fury"],
    "think": ["thinking", "hmm", "consider"],
    "love": ["heart", "romance", "affection"],
    "money": ["dollar", "cash", "rich", "currency"],
    "time": ["clock", "watch", "hour"],
    "food": ["eat", "meal", "hungry"],
    "drink": ["beverage", "cup", "glass"],
    "animal": ["pet", "creature", "wildlife"],
    "plant": ["flower", "tree", "nature", "leaf"],
    "weather": ["sun", "rain", "cloud", "snow"],
    "sport": ["ball", "game", "athletic"],
    "travel": ["car", "plane", "train", "vacation"],
    "work": ["office", "job", "business"],
    "home": ["house", "building", "residence"],
    "tech": ["computer", "phone", "device"],
    "art": ["paint", "draw", "creative"],
    "science": ["lab", "experiment", "research"],
}


@lru_cache(maxsize=1)
def _load_emoji_metadata() -> list[dict]:
    """Load emoji metadata from openmoji.json.

    Returns:
        List of emoji dicts with hexcode, annotation, tags, group, etc.
    """
    if not METADATA_FILE.exists():
        return []

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        return []


@lru_cache(maxsize=1)
def _build_emoji_index() -> tuple[list[dict], dict[str, dict]]:
    """Build searchable emoji list and lookup map.

    Returns:
        Tuple of (emoji_list, hexcode_map)
    """
    raw_data = _load_emoji_metadata()

    emoji_list = []
    hexcode_map = {}

    for item in raw_data:
        hexcode = item.get("hexcode", "")
        if not hexcode:
            continue

        # Check if SVG file exists
        svg_path = EMOJI_DIR / f"{hexcode}.svg"
        if not svg_path.exists():
            continue

        # Build keywords from tags and annotation
        keywords = []

        # Add annotation words
        annotation = item.get("annotation", "")
        if annotation:
            keywords.extend(annotation.lower().split())

        # Add tags
        tags = item.get("tags", "")
        if tags:
            keywords.extend([t.strip().lower() for t in tags.split(",") if t.strip()])

        # Add openmoji_tags
        openmoji_tags = item.get("openmoji_tags", "")
        if openmoji_tags:
            keywords.extend([t.strip().lower() for t in openmoji_tags.split(",") if t.strip()])

        # Add group/subgroup
        group = item.get("group", "")
        subgroups = item.get("subgroups", "")
        if group:
            keywords.extend(group.lower().replace("-", " ").split())
        if subgroups:
            keywords.extend(subgroups.lower().replace("-", " ").split())

        # Deduplicate keywords
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw and kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        emoji = {
            "hexcode": hexcode,
            "emoji": item.get("emoji", ""),
            "name": annotation,
            "keywords": unique_keywords,
            "group": group,
            "subgroup": subgroups,
        }

        emoji_list.append(emoji)
        hexcode_map[hexcode] = emoji

    return emoji_list, hexcode_map


def get_all_emoji() -> list[dict]:
    """Get all available emoji.

    Returns:
        List of emoji dicts
    """
    emoji_list, _ = _build_emoji_index()
    return emoji_list


def get_emoji_map() -> dict[str, dict]:
    """Get hexcode -> emoji mapping.

    Returns:
        Dict mapping hexcode to emoji dict
    """
    _, hexcode_map = _build_emoji_index()
    return hexcode_map


def search_emoji(query: str, limit: int = 60) -> list[dict]:
    """Search emoji by name or keywords.

    Args:
        query: Search term (searches name and keywords)
        limit: Maximum results

    Returns:
        List of matching emoji dicts
    """
    emoji_list, _ = _build_emoji_index()

    if not query:
        # Return popular/common emoji first
        return emoji_list[:limit]

    query = query.lower().strip()
    query_parts = query.split()

    # Expand query with aliases
    expanded_parts = []
    for part in query_parts:
        expanded_parts.append(part)
        if part in SEARCH_ALIASES:
            expanded_parts.extend(SEARCH_ALIASES[part])

    results = []
    scores = []  # Track match quality for sorting

    for emoji in emoji_list:
        score = 0
        matches_all = True

        for part in query_parts:
            found = False
            part_score = 0

            # Check name (exact match = higher score)
            name_lower = emoji["name"].lower()
            if part in name_lower:
                found = True
                if name_lower.startswith(part):
                    part_score = 3  # Starts with = best
                elif f" {part}" in f" {name_lower}":
                    part_score = 2  # Word match
                else:
                    part_score = 1  # Contains

            # Check keywords
            if not found:
                for keyword in emoji["keywords"]:
                    if part in keyword:
                        found = True
                        if keyword == part:
                            part_score = 2  # Exact keyword match
                        elif keyword.startswith(part):
                            part_score = 1.5
                        else:
                            part_score = 1
                        break

            # Check expanded aliases
            if not found:
                for alias in expanded_parts:
                    if alias in emoji["name"].lower():
                        found = True
                        part_score = 0.5
                        break
                    for keyword in emoji["keywords"]:
                        if alias in keyword:
                            found = True
                            part_score = 0.5
                            break
                    if found:
                        break

            if not found:
                matches_all = False
                break

            score += part_score

        if matches_all:
            results.append(emoji)
            scores.append(score)
            if len(results) >= limit * 2:  # Get extra for sorting
                break

    # Sort by score (descending) and return top results
    # Use key function to avoid comparing dicts when scores are equal
    sorted_results = [e for _, e in sorted(zip(scores, results), key=lambda x: x[0], reverse=True)]
    return sorted_results[:limit]


def get_emoji_url(hexcode: str) -> str:
    """Get URL path for an emoji SVG.

    Args:
        hexcode: Emoji hexcode (e.g., "1F600")

    Returns:
        URL path to SVG
    """
    return f"/static/emoji/{hexcode}.svg"


def is_valid_emoji(hexcode: str) -> bool:
    """Check if emoji hexcode is valid.

    Args:
        hexcode: Emoji hexcode

    Returns:
        True if emoji exists
    """
    _, hexcode_map = _build_emoji_index()
    return hexcode in hexcode_map


def get_emoji_groups() -> list[str]:
    """Get all emoji group names.

    Returns:
        Sorted list of group names
    """
    emoji_list, _ = _build_emoji_index()
    groups = set()
    for emoji in emoji_list:
        if emoji["group"]:
            groups.add(emoji["group"])
    return sorted(groups)


def get_emoji_by_group(group: str, limit: int = 100) -> list[dict]:
    """Get emoji filtered by group.

    Args:
        group: Group name
        limit: Maximum results

    Returns:
        List of emoji in that group
    """
    emoji_list, _ = _build_emoji_index()
    results = []

    for emoji in emoji_list:
        if emoji["group"] == group:
            results.append(emoji)
            if len(results) >= limit:
                break

    return results
