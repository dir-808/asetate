"""Pixel icon manifest for crate icons.

Dynamically scans PNG files from static/icons/ directory and generates
searchable keywords from filenames.

Filename format: Category_Keyword1_Keyword2_..._KeywordN.png
Example: Alchemy_Element_Fire.png -> keywords: [alchemy, element, fire]

Icons are from various pixel art packs (CC0/public domain).
"""

from functools import lru_cache
from pathlib import Path

# Path to icons directory (relative to this file)
ICONS_DIR = Path(__file__).parent.parent / "static" / "icons"

# Default icon when none selected
DEFAULT_ICON = "Software_File_Folder_Directory_Explorer"

# Common word expansions for better search
KEYWORD_EXPANSIONS = {
    "sw": ["southwest"],
    "se": ["southeast"],
    "nw": ["northwest"],
    "ne": ["northeast"],
    "n": ["north"],
    "s": ["south"],
    "e": ["east"],
    "w": ["west"],
    "ui": ["interface", "user interface"],
    "rpg": ["game", "gaming", "role playing"],
    "dj": ["music", "vinyl", "turntable"],
    "fx": ["effects", "special effects"],
    "hp": ["health", "hitpoints"],
    "mp": ["mana", "magic points"],
    "xp": ["experience"],
    "ai": ["artificial intelligence"],
    "pc": ["computer", "personal computer"],
    "tv": ["television"],
    "cd": ["compact disc", "disc"],
    "dvd": ["disc", "video"],
    "usb": ["drive", "storage"],
    "hdd": ["hard drive", "storage"],
    "ssd": ["solid state", "storage"],
    "wifi": ["wireless", "internet", "network"],
    "lan": ["network", "ethernet"],
    "vpn": ["network", "secure"],
    "pdf": ["document", "file"],
    "jpg": ["image", "photo"],
    "png": ["image", "picture"],
    "gif": ["animation", "image"],
    "mp3": ["audio", "music"],
    "wav": ["audio", "sound"],
    "avi": ["video", "movie"],
    "zip": ["archive", "compressed"],
    "exe": ["program", "application"],
    "dll": ["library", "system"],
    "ios": ["apple", "iphone", "mobile"],
    "macos": ["apple", "mac", "computer"],
    "ipados": ["apple", "ipad", "tablet"],
    "ok": ["okay", "confirm", "yes"],
}

# Synonyms to add as extra keywords
CATEGORY_SYNONYMS = {
    "alchemy": ["magic", "potion", "mystical", "fantasy"],
    "arrows": ["direction", "navigation", "pointer"],
    "boardgames": ["game", "tabletop", "board"],
    "controller": ["gamepad", "gaming", "button", "input"],
    "cosmetics": ["beauty", "makeup", "fashion"],
    "emoji": ["face", "emotion", "expression", "smiley"],
    "food": ["eat", "drink", "meal", "snack"],
    "hats": ["headwear", "fashion", "accessory"],
    "map": ["location", "navigation", "place", "marker"],
    "media": ["audio", "video", "music", "sound"],
    "misc": ["miscellaneous", "other", "various"],
    "platforms": ["brand", "logo", "social", "app"],
    "rpg": ["game", "fantasy", "adventure", "item", "weapon"],
    "software": ["app", "application", "program", "computer"],
    "sports": ["athletics", "exercise", "fitness", "game"],
    "tools": ["utility", "work", "equipment", "hardware"],
    "travel": ["transport", "vehicle", "journey", "trip"],
    "warfare": ["military", "weapon", "combat", "battle"],
    "weather": ["climate", "sky", "nature", "forecast"],
}


def _parse_filename(filename: str) -> dict:
    """Parse an icon filename into name and keywords.

    Args:
        filename: The PNG filename (e.g., "Alchemy_Element_Fire.png")

    Returns:
        Dict with 'name' (without extension) and 'keywords' list
    """
    # Remove .png extension
    name = filename[:-4] if filename.endswith(".png") else filename

    # Split on underscores
    parts = name.split("_")

    # Build keywords from parts (lowercase)
    keywords = []
    for part in parts:
        lower_part = part.lower()
        keywords.append(lower_part)

        # Add expansions if available
        if lower_part in KEYWORD_EXPANSIONS:
            keywords.extend(KEYWORD_EXPANSIONS[lower_part])

    # Add category synonyms
    if parts and parts[0].lower() in CATEGORY_SYNONYMS:
        keywords.extend(CATEGORY_SYNONYMS[parts[0].lower()])

    # Deduplicate while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return {
        "name": name,
        "keywords": unique_keywords,
    }


@lru_cache(maxsize=1)
def _scan_icons_directory() -> list[dict]:
    """Scan the icons directory and build the icon manifest.

    Returns:
        List of icon dicts with 'name' and 'keywords'
    """
    icons = []

    if not ICONS_DIR.exists():
        return icons

    for filepath in sorted(ICONS_DIR.glob("*.png")):
        icon = _parse_filename(filepath.name)
        icons.append(icon)

    return icons


def get_all_icons() -> list[dict]:
    """Get all available icons.

    Returns:
        List of icon dicts with 'name' and 'keywords'
    """
    return _scan_icons_directory()


# For backwards compatibility - lazy loaded
@property
def _pixel_icons():
    return get_all_icons()


# Module-level access (computed on first access)
PIXEL_ICONS = None


def _ensure_loaded():
    """Ensure PIXEL_ICONS is loaded."""
    global PIXEL_ICONS
    if PIXEL_ICONS is None:
        PIXEL_ICONS = get_all_icons()


# Quick lookup by icon name (lazy loaded)
_PIXEL_ICON_MAP = None


def get_icon_map() -> dict:
    """Get the icon name -> icon dict mapping."""
    global _PIXEL_ICON_MAP
    if _PIXEL_ICON_MAP is None:
        _ensure_loaded()
        _PIXEL_ICON_MAP = {icon["name"]: icon for icon in PIXEL_ICONS}
    return _PIXEL_ICON_MAP


def search_icons(query: str, limit: int = 50) -> list[dict]:
    """Search icons by name or keywords.

    Args:
        query: Search term (searches name and keywords)
        limit: Maximum number of results to return

    Returns:
        List of matching icon dictionaries
    """
    _ensure_loaded()

    if not query:
        return PIXEL_ICONS[:limit]

    query = query.lower().strip()
    query_parts = query.split()
    results = []

    for icon in PIXEL_ICONS:
        # Check if all query parts match somewhere
        matches_all = True
        for part in query_parts:
            found = False
            # Check name
            if part in icon["name"].lower():
                found = True
            else:
                # Check keywords
                for keyword in icon["keywords"]:
                    if part in keyword:
                        found = True
                        break

            if not found:
                matches_all = False
                break

        if matches_all:
            results.append(icon)
            if len(results) >= limit:
                break

    return results


def get_icon_url(icon_name: str) -> str:
    """Get the URL path for an icon.

    Args:
        icon_name: The icon filename (without extension)

    Returns:
        URL path to the icon PNG file
    """
    return f"/static/icons/{icon_name}.png"


def is_valid_icon(icon_name: str) -> bool:
    """Check if an icon name is valid.

    Args:
        icon_name: The icon name to validate

    Returns:
        True if the icon exists
    """
    icon_map = get_icon_map()
    return icon_name in icon_map


def get_categories() -> list[str]:
    """Get all unique icon categories.

    Returns:
        Sorted list of category names
    """
    _ensure_loaded()
    categories = set()
    for icon in PIXEL_ICONS:
        # First part of name is category
        parts = icon["name"].split("_")
        if parts:
            categories.add(parts[0])
    return sorted(categories)


def get_icons_by_category(category: str, limit: int = 100) -> list[dict]:
    """Get icons filtered by category.

    Args:
        category: Category name (e.g., "Alchemy", "Software")
        limit: Maximum results

    Returns:
        List of icons in that category
    """
    _ensure_loaded()
    results = []
    category_lower = category.lower()

    for icon in PIXEL_ICONS:
        if icon["name"].lower().startswith(category_lower + "_"):
            results.append(icon)
            if len(results) >= limit:
                break

    return results


# Initialize on module load for backwards compatibility
_ensure_loaded()
