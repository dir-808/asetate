"""OpenMoji emoji icons for crate icons.

Loads emoji metadata from openmoji.json and provides search functionality.
Filtered to only include emoji supported by Noto Emoji font (monochrome).

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

# Noto Emoji font supported characters (curated list)
# Only these will appear in the picker to ensure monochrome rendering
# Hexcodes for common emoji known to work with Noto Emoji font
NOTO_EMOJI_SUPPORTED = {
    # Faces & Expressions
    "1F600", "1F601", "1F602", "1F603", "1F604", "1F605", "1F606", "1F607",
    "1F608", "1F609", "1F60A", "1F60B", "1F60C", "1F60D", "1F60E", "1F60F",
    "1F610", "1F611", "1F612", "1F613", "1F614", "1F615", "1F616", "1F617",
    "1F618", "1F619", "1F61A", "1F61B", "1F61C", "1F61D", "1F61E", "1F61F",
    "1F620", "1F621", "1F622", "1F623", "1F624", "1F625", "1F626", "1F627",
    "1F628", "1F629", "1F62A", "1F62B", "1F62C", "1F62D", "1F62E", "1F62F",
    "1F630", "1F631", "1F632", "1F633", "1F634", "1F635", "1F636", "1F637",
    "1F641", "1F642", "1F643", "1F644", "1F910", "1F911", "1F912", "1F913",
    "1F914", "1F915", "1F917", "1F920", "1F921", "1F922", "1F923", "1F924",
    "1F925", "1F927", "1F928", "1F929", "1F92A", "1F92B", "1F92C", "1F92D",
    "1F92E", "1F92F", "1F970", "1F971", "1F972", "1F973", "1F974", "1F975",
    "1F976", "1F978", "1F979", "1F97A",
    # Gestures & Body
    "1F44D", "1F44E", "1F44C", "1F44A", "270A", "270B", "270C", "1F44B",
    "1F44F", "1F450", "1F64C", "1F64F", "1F91D", "1F91E", "1F91F", "1F918",
    "1F919", "1F91A", "1F91B", "1F91C", "1F590", "261D", "1F446", "1F447",
    "1F448", "1F449", "1F4AA", "1F9B5", "1F9B6", "1F442", "1F443", "1F440",
    "1F441", "1F445", "1F444", "1F48B", "1F463", "1F9E0", "1F9B7", "1F9B4",
    # Hearts & Symbols
    "2764", "1F494", "1F495", "1F496", "1F497", "1F498", "1F499", "1F49A",
    "1F49B", "1F49C", "1F49D", "1F49E", "1F49F", "1F5A4", "1F90D", "1F90E",
    "1F9E1", "2763", "2665", "2661",
    # Stars & Sparkles
    "2B50", "1F31F", "1F320", "2728", "1F4AB", "1FA90",
    # Fire & Weather
    "1F525", "2744", "1F4A7", "1F4A6", "1F327", "1F328", "1F329", "26C8",
    "1F32A", "1F32B", "1F32C", "2600", "1F324", "26C5", "1F325", "1F326",
    "1F308", "2614", "26A1", "2604", "1F30A",
    # Nature & Animals
    "1F436", "1F431", "1F42D", "1F439", "1F430", "1F98A", "1F43B", "1F43C",
    "1F428", "1F42F", "1F981", "1F984", "1F42E", "1F437", "1F43D", "1F438",
    "1F435", "1F648", "1F649", "1F64A", "1F412", "1F414", "1F427", "1F426",
    "1F424", "1F423", "1F425", "1F986", "1F985", "1F989", "1F987", "1F43A",
    "1F417", "1F434", "1F40E", "1F98C", "1F42A", "1F42B", "1F992", "1F418",
    "1F98F", "1F99B", "1F42D", "1F401", "1F400", "1F439", "1F430", "1F407",
    "1F43F", "1F994", "1F987", "1F43B", "1F428", "1F43C", "1F998", "1F9A1",
    "1F43E", "1F983", "1F54A", "1F99A", "1F99C", "1F9A2", "1F9A9", "1F9AE",
    "1F40A", "1F422", "1F98E", "1F40D", "1F432", "1F409", "1F995", "1F996",
    "1F433", "1F40B", "1F42C", "1F9AD", "1F41F", "1F420", "1F421", "1F988",
    "1F419", "1F41A", "1F40C", "1F98B", "1F41B", "1F41C", "1F41D", "1F41E",
    "1F997", "1F577", "1F578", "1F982", "1F99F",
    # Plants & Flowers
    "1F490", "1F338", "1F4AE", "1F3F5", "1F339", "1F940", "1F33A", "1F33B",
    "1F33C", "1F337", "1F331", "1F332", "1F333", "1F334", "1F335", "1F33E",
    "1F33F", "2618", "1F340", "1F341", "1F342", "1F343", "1FAB4", "1FAB5",
    # Food & Drink
    "1F347", "1F348", "1F349", "1F34A", "1F34B", "1F34C", "1F34D", "1F96D",
    "1F34E", "1F34F", "1F350", "1F351", "1F352", "1F353", "1FAD0", "1F95D",
    "1F345", "1FAD2", "1F965", "1F951", "1F346", "1F954", "1F955", "1F33D",
    "1F336", "1FAD1", "1F952", "1F96C", "1F966", "1F9C4", "1F9C5", "1F344",
    "1F95C", "1F330", "1F35E", "1F950", "1F956", "1FAD3", "1F968", "1F96F",
    "1F95E", "1F9C7", "1F9C0", "1F356", "1F357", "1F969", "1F953", "1F354",
    "1F35F", "1F355", "1F32D", "1F96A", "1F32E", "1F32F", "1FAD4", "1F959",
    "1F9C6", "1F95A", "1F373", "1F958", "1F372", "1FAD5", "1F963", "1F957",
    "1F37F", "1F9C8", "1F9C2", "1F96B", "1F371", "1F358", "1F359", "1F35A",
    "1F35B", "1F35C", "1F35D", "1F360", "1F362", "1F363", "1F364", "1F365",
    "1F96E", "1F361", "1F95F", "1F960", "1F961", "1F980", "1F99E", "1F990",
    "1F991", "1F9AA", "1F366", "1F367", "1F368", "1F369", "1F36A", "1F382",
    "1F370", "1F9C1", "1F967", "1F36B", "1F36C", "1F36D", "1F36E", "1F36F",
    "1F37C", "1F95B", "2615", "1FAD6", "1F375", "1F376", "1F37E", "1F377",
    "1F378", "1F379", "1F37A", "1F37B", "1F942", "1F943", "1FAD7", "1F964",
    "1F9CB", "1F9C3", "1F9C9", "1F9CA", "1F962", "1F37D", "1F944", "1F374",
    "1F52A",
    # Activities & Sports
    "26BD", "1F3C0", "1F3C8", "26BE", "1F94E", "1F3BE", "1F3D0", "1F3C9",
    "1F94F", "1F3B1", "1F3D3", "1F3F8", "1F94D", "1F3D2", "1F3D1", "1F94B",
    "1F3CF", "1F945", "26F3", "1F94C", "1F3AF", "1F3A3", "1F93F", "1F3BF",
    "1F6F7", "1F94A", "1F94C", "1F3CB", "1F93C", "1F938", "1F93D", "1F93E",
    "1F3C4", "1F6A3", "1F3CA", "26F9", "1F6B4", "1F6B5", "1F3C7", "1F9D8",
    "1F3C6", "1F396", "1F947", "1F948", "1F949",
    # Music & Art
    "1F3A4", "1F3A7", "1F3B5", "1F3B6", "1F3B7", "1F3B8", "1F3B9", "1F3BA",
    "1F3BB", "1FA95", "1F941", "1FA98", "1F3A8", "1F3AD", "1F3AC", "1F4F7",
    "1F4F8", "1F4F9", "1F4FA", "1F4FB", "1F4FC",
    # Objects & Tools
    "1F4BF", "1F4C0", "1F4BD", "1F4BE", "1F4BF", "1F4C0", "1F50A", "1F508",
    "1F509", "1F507", "1F4E2", "1F4E3", "1F514", "1F515", "1F3BC", "1F4F1",
    "1F4F2", "260E", "1F4DE", "1F4DF", "1F4E0", "1F50B", "1F50C", "1F4BB",
    "1F5A5", "1F5A8", "1F5B1", "1F5B2", "1F4BD", "1F4BE", "1F4BF", "1F4C0",
    "1F50D", "1F50E", "1F56F", "1F4A1", "1F526", "1F3EE", "1FA94", "1F4D4",
    "1F4D5", "1F4D6", "1F4D7", "1F4D8", "1F4D9", "1F4DA", "1F4D3", "1F4D2",
    "1F4C3", "1F4DC", "1F4C4", "1F4F0", "1F5DE", "1F4D1", "1F516", "1F3F7",
    "1F4B0", "1FA99", "1F4B4", "1F4B5", "1F4B6", "1F4B7", "1F4B8", "1F4B3",
    "1F9FE", "1F4B9", "2709", "1F4E7", "1F4E8", "1F4E9", "1F4E4", "1F4E5",
    "1F4E6", "1F4EB", "1F4EA", "1F4EC", "1F4ED", "1F4EE", "1F5F3", "270F",
    "2712", "1F58B", "1F58A", "1F58C", "1F58D", "1F4DD", "1F4BC", "1F4C1",
    "1F4C2", "1F5C2", "1F4C5", "1F4C6", "1F5D2", "1F5D3", "1F4C7", "1F4C8",
    "1F4C9", "1F4CA", "1F4CB", "1F4CC", "1F4CD", "1F4CE", "1F587", "1F4CF",
    "1F4D0", "2702", "1F5C3", "1F5C4", "1F5D1", "1F512", "1F513", "1F50F",
    "1F510", "1F511", "1F5DD", "1F528", "1FA93", "26CF", "2692", "1F6E0",
    "1F5E1", "2694", "1F52B", "1FA83", "1F3F9", "1F6E1", "1FA9A", "1F527",
    "1FA9B", "1F529", "2699", "1F5DC", "2696", "1F9AF", "1F517", "26D3",
    "1FA9D", "1F9F0", "1F9F2", "1FA9C", "2697", "1F9EA", "1F9EB", "1F9EC",
    "1F52C", "1F52D", "1F4E1", "1F489", "1FA78", "1F48A", "1FA79", "1FA7C",
    "1FA7A", "1FA7B", "1F6CF", "1FA91", "1F6CB", "1FA91", "1F6BD", "1FAA0",
    "1F6BF", "1F6C1", "1FA92", "1FA9E", "1FA9F", "1FAA0", "1FAA1", "1FAA2",
    # Symbols & Arrows
    "2714", "2716", "2795", "2796", "2797", "27B0", "27BF", "2733", "2734",
    "2747", "203C", "2049", "2753", "2754", "2755", "2757", "2763", "2764",
    "1F4AF", "1F4A2", "1F4A5", "1F4A6", "1F4A8", "1F573", "1F4A3", "1F4AC",
    "1F5E8", "1F441-FE0F-200D-1F5E8-FE0F", "1F5EF", "1F4AD", "1F4A4",
    "1F504", "1F503", "1F519", "1F51A", "1F51B", "1F51C", "1F51D", "1F6D0",
    "269B", "1F549", "2721", "2638", "262F", "271D", "2626", "262A", "262E",
    "1F54E", "1F52F", "1FAAF", "26CE", "2648", "2649", "264A", "264B",
    "264C", "264D", "264E", "264F", "2650", "2651", "2652", "2653",
    # Buildings & Places
    "1F3E0", "1F3E1", "1F3E2", "1F3E3", "1F3E4", "1F3E5", "1F3E6", "1F3E7",
    "1F3E8", "1F3E9", "1F3EA", "1F3EB", "1F3EC", "1F3ED", "1F3EF", "1F3F0",
    "1F492", "1F5FC", "1F5FD", "26EA", "1F54C", "1F6D5", "1F54D", "26E9",
    "1F54B", "26F2", "26FA", "1F301", "1F303", "1F3D9", "1F304", "1F305",
    "1F306", "1F307", "1F309", "1F3A0", "1F3A1", "1F3A2", "1F488", "1F3AA",
    # Transport
    "1F697", "1F695", "1F699", "1F68C", "1F68E", "1F3CE", "1F693", "1F691",
    "1F692", "1F690", "1F69A", "1F69B", "1F69C", "1F3CD", "1F6B2", "1F6F4",
    "1F6F5", "1F68F", "1F6E3", "1F6E4", "26FD", "1F6A8", "1F6A5", "1F6A6",
    "1F6A7", "26A0", "1F6D1", "1F6A7", "2693", "26F5", "1F6A4", "1F6F3",
    "26F4", "1F6E5", "1F6A2", "2708", "1F6E9", "1F6EB", "1F6EC", "1FA82",
    "1F4BA", "1F681", "1F682", "1F683", "1F684", "1F685", "1F686", "1F687",
    "1F688", "1F689", "1F68A", "1F69D", "1F69E", "1F680", "1F6F8", "1F6F0",
    "1F6CE", "1F9F3",
    # Celestial & Time
    "1F311", "1F312", "1F313", "1F314", "1F315", "1F316", "1F317", "1F318",
    "1F319", "1F31A", "1F31B", "1F31C", "1F321", "2600", "1F31D", "1F31E",
    "1FA90", "2B50", "1F31F", "1F320", "1F30C", "2601", "26C5", "26C8",
    "1F324", "1F325", "1F326", "1F327", "1F328", "1F329", "1F32A", "1F32B",
    "1F32C", "1F300", "1F308", "1F302", "2602", "26F1", "26A1", "2744",
    "2603", "26C4", "2604", "1F525", "1F4A7", "1F30A", "1F570", "1F55B",
    "1F550", "1F551", "1F552", "1F553", "1F554", "1F555", "1F556", "1F557",
    "1F558", "1F559", "1F55A", "231A", "23F0", "23F1", "23F2", "1F4C5",
    "1F4C6", "1F4C7",
    # Flags & Globe
    "1F30D", "1F30E", "1F30F", "1F310", "1F5FA", "1F3F3", "1F3F4", "1F3C1",
    # Gaming & Recreation
    "1F3AE", "1F579", "1F3B0", "1F3B2", "265F", "1FA80", "1FA81", "1F9E9",
    "1F9F8", "1FA86", "1FA85", "1F3AD", "1F3A8", "1F9F5", "1FAA1", "1FAA2",
    # Misc Objects
    "1F48E", "1F451", "1F452", "1F3A9", "1F393", "1F9E2", "26D1", "1F4FF",
    "1F484", "1F48D", "1F48E", "1F4E6", "1F381", "1F380", "1F386", "1F387",
    "1F9E7", "1F388", "1F389", "1F38A", "1F38B", "1F38D", "1F38E", "1F38F",
    "1F390", "1F391", "1F9E8", "1F3EE",
    # Additional common emoji
    "1F480", "1F4A9", "1F47B", "1F47D", "1F916", "1F383", "1F47E", "1F47F",
    "1F5FF", "1F9D0", "1F9DF", "1F9DB", "1F9DC", "1F9DE", "1F9DD", "1F9DA",
    "1F9B8", "1F9B9", "1F9D9", "1F9D1", "1F468", "1F469", "1F467", "1F466",
    "1F476", "1F474", "1F475", "1F9D3", "1F9D4", "1F9D2",
}

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

    Only includes emoji that are in NOTO_EMOJI_SUPPORTED to ensure
    monochrome rendering via Noto Emoji font.

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

        # Only include emoji that are in Noto Emoji font
        if hexcode not in NOTO_EMOJI_SUPPORTED:
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
