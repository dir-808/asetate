"""Pixel icon manifest for crate icons.

Uses 1-bit pixel icons from the Nikoichu icon pack (CC0 license).
Download from: https://nikoichu.itch.io/pixel-icons

Place PNG files in: asetate/static/icons/
Icons are 16x16 pixels, black on transparent background.
"""

# Icon manifest: each icon has a filename (without extension) and search keywords
# Keywords are used for the searchable icon picker
PIXEL_ICONS = [
    # Music & Audio
    {"name": "music", "keywords": ["music", "note", "audio", "sound", "song", "tune"]},
    {"name": "music-alt", "keywords": ["music", "note", "audio", "sound", "song", "tune", "double"]},
    {"name": "headphones", "keywords": ["headphones", "audio", "listen", "music", "dj", "monitor"]},
    {"name": "speaker", "keywords": ["speaker", "audio", "sound", "volume", "loud", "bass"]},
    {"name": "volume", "keywords": ["volume", "sound", "audio", "speaker", "loud"]},
    {"name": "volume-mute", "keywords": ["mute", "silent", "quiet", "volume", "off"]},
    {"name": "microphone", "keywords": ["microphone", "mic", "record", "voice", "vocal", "sing"]},
    {"name": "radio", "keywords": ["radio", "broadcast", "fm", "am", "station", "tune"]},

    # Playback Controls
    {"name": "play", "keywords": ["play", "start", "go", "begin", "run"]},
    {"name": "pause", "keywords": ["pause", "stop", "wait", "hold"]},
    {"name": "stop", "keywords": ["stop", "end", "halt", "finish"]},
    {"name": "forward", "keywords": ["forward", "next", "skip", "fast"]},
    {"name": "backward", "keywords": ["backward", "previous", "rewind", "back"]},
    {"name": "repeat", "keywords": ["repeat", "loop", "again", "cycle"]},
    {"name": "shuffle", "keywords": ["shuffle", "random", "mix", "scramble"]},

    # Folders & Organization
    {"name": "folder", "keywords": ["folder", "directory", "organize", "crate", "box", "container"]},
    {"name": "folder-open", "keywords": ["folder", "open", "directory", "organize"]},
    {"name": "folder-plus", "keywords": ["folder", "add", "new", "plus", "create"]},
    {"name": "archive", "keywords": ["archive", "box", "storage", "crate", "container", "package"]},
    {"name": "box", "keywords": ["box", "crate", "container", "package", "storage"]},
    {"name": "inbox", "keywords": ["inbox", "tray", "receive", "incoming"]},

    # Favorites & Ratings
    {"name": "heart", "keywords": ["heart", "love", "favorite", "like", "fav"]},
    {"name": "heart-empty", "keywords": ["heart", "love", "favorite", "like", "outline"]},
    {"name": "star", "keywords": ["star", "favorite", "rating", "best", "top", "featured"]},
    {"name": "star-empty", "keywords": ["star", "favorite", "rating", "outline"]},
    {"name": "bookmark", "keywords": ["bookmark", "save", "mark", "flag", "remember"]},
    {"name": "flag", "keywords": ["flag", "mark", "important", "attention", "notice"]},

    # Energy & Mood
    {"name": "fire", "keywords": ["fire", "hot", "flame", "trending", "popular", "heat", "burn", "energy"]},
    {"name": "lightning", "keywords": ["lightning", "bolt", "electric", "energy", "power", "fast", "zap"]},
    {"name": "sun", "keywords": ["sun", "day", "bright", "light", "summer", "warm", "sunny"]},
    {"name": "moon", "keywords": ["moon", "night", "dark", "evening", "late", "chill"]},
    {"name": "cloud", "keywords": ["cloud", "weather", "sky", "dreamy", "soft"]},
    {"name": "rain", "keywords": ["rain", "weather", "water", "sad", "melancholy", "drops"]},
    {"name": "snow", "keywords": ["snow", "winter", "cold", "ice", "frozen", "chill"]},
    {"name": "wind", "keywords": ["wind", "air", "breeze", "flow", "movement"]},

    # Nature & Vibes
    {"name": "tree", "keywords": ["tree", "nature", "forest", "organic", "green", "wood"]},
    {"name": "leaf", "keywords": ["leaf", "nature", "plant", "organic", "green", "eco"]},
    {"name": "flower", "keywords": ["flower", "plant", "nature", "bloom", "spring", "pretty"]},
    {"name": "mountain", "keywords": ["mountain", "peak", "climb", "high", "epic", "adventure"]},
    {"name": "wave", "keywords": ["wave", "water", "ocean", "sea", "surf", "beach", "summer"]},
    {"name": "drop", "keywords": ["drop", "water", "liquid", "rain", "tear", "wet"]},

    # Objects & Items
    {"name": "diamond", "keywords": ["diamond", "gem", "jewel", "precious", "rare", "valuable", "crystal"]},
    {"name": "crown", "keywords": ["crown", "king", "queen", "royal", "best", "top", "vip"]},
    {"name": "trophy", "keywords": ["trophy", "award", "winner", "champion", "prize", "best"]},
    {"name": "medal", "keywords": ["medal", "award", "achievement", "winner", "prize"]},
    {"name": "key", "keywords": ["key", "unlock", "access", "secret", "password", "open"]},
    {"name": "lock", "keywords": ["lock", "secure", "private", "protected", "closed"]},
    {"name": "gift", "keywords": ["gift", "present", "surprise", "special", "reward"]},
    {"name": "coin", "keywords": ["coin", "money", "gold", "currency", "cash", "valuable"]},
    {"name": "gem", "keywords": ["gem", "crystal", "jewel", "precious", "rare"]},

    # Tags & Labels
    {"name": "tag", "keywords": ["tag", "label", "price", "category", "mark"]},
    {"name": "label", "keywords": ["label", "tag", "name", "title", "mark"]},
    {"name": "ticket", "keywords": ["ticket", "pass", "entry", "event", "show", "concert"]},

    # Time & Calendar
    {"name": "clock", "keywords": ["clock", "time", "hour", "schedule", "watch"]},
    {"name": "alarm", "keywords": ["alarm", "alert", "wake", "reminder", "time"]},
    {"name": "calendar", "keywords": ["calendar", "date", "schedule", "event", "plan"]},
    {"name": "hourglass", "keywords": ["hourglass", "time", "wait", "timer", "sand"]},

    # Communication
    {"name": "chat", "keywords": ["chat", "message", "talk", "conversation", "comment"]},
    {"name": "mail", "keywords": ["mail", "email", "letter", "message", "send"]},
    {"name": "bell", "keywords": ["bell", "notification", "alert", "ring", "alarm"]},

    # Actions
    {"name": "check", "keywords": ["check", "done", "complete", "yes", "ok", "approved"]},
    {"name": "cross", "keywords": ["cross", "close", "delete", "remove", "no", "cancel"]},
    {"name": "plus", "keywords": ["plus", "add", "new", "create", "more"]},
    {"name": "minus", "keywords": ["minus", "remove", "less", "subtract"]},
    {"name": "search", "keywords": ["search", "find", "look", "magnify", "zoom"]},
    {"name": "filter", "keywords": ["filter", "sort", "organize", "refine"]},

    # Arrows & Navigation
    {"name": "arrow-up", "keywords": ["arrow", "up", "rise", "increase", "upload"]},
    {"name": "arrow-down", "keywords": ["arrow", "down", "fall", "decrease", "download"]},
    {"name": "arrow-left", "keywords": ["arrow", "left", "back", "previous"]},
    {"name": "arrow-right", "keywords": ["arrow", "right", "forward", "next"]},

    # People & Characters
    {"name": "user", "keywords": ["user", "person", "profile", "account", "human"]},
    {"name": "users", "keywords": ["users", "people", "group", "team", "community"]},
    {"name": "skull", "keywords": ["skull", "death", "dark", "danger", "halloween", "spooky", "hardcore"]},
    {"name": "ghost", "keywords": ["ghost", "spooky", "halloween", "spirit", "haunted"]},
    {"name": "robot", "keywords": ["robot", "bot", "machine", "ai", "tech", "electronic"]},
    {"name": "alien", "keywords": ["alien", "space", "ufo", "extraterrestrial", "weird"]},

    # Expressions & Emoji-style
    {"name": "smile", "keywords": ["smile", "happy", "joy", "good", "positive", "face"]},
    {"name": "sad", "keywords": ["sad", "unhappy", "frown", "negative", "face"]},
    {"name": "wink", "keywords": ["wink", "playful", "fun", "cheeky", "face"]},
    {"name": "cool", "keywords": ["cool", "sunglasses", "awesome", "chill", "face"]},
    {"name": "angry", "keywords": ["angry", "mad", "rage", "upset", "face"]},
    {"name": "love-eyes", "keywords": ["love", "heart", "eyes", "crush", "adore", "face"]},
    {"name": "surprised", "keywords": ["surprised", "wow", "shock", "amazed", "face"]},
    {"name": "thinking", "keywords": ["thinking", "hmm", "wonder", "ponder", "face"]},

    # Symbols
    {"name": "circle", "keywords": ["circle", "dot", "round", "shape"]},
    {"name": "square", "keywords": ["square", "box", "shape", "block"]},
    {"name": "triangle", "keywords": ["triangle", "shape", "point"]},
    {"name": "hexagon", "keywords": ["hexagon", "shape", "six", "honeycomb"]},
    {"name": "infinity", "keywords": ["infinity", "forever", "endless", "loop", "eternal"]},
    {"name": "yin-yang", "keywords": ["yin", "yang", "balance", "harmony", "zen"]},

    # Tech & Devices
    {"name": "computer", "keywords": ["computer", "pc", "desktop", "monitor", "screen"]},
    {"name": "laptop", "keywords": ["laptop", "computer", "portable", "notebook"]},
    {"name": "phone", "keywords": ["phone", "mobile", "cell", "smartphone", "call"]},
    {"name": "camera", "keywords": ["camera", "photo", "picture", "image", "snap"]},
    {"name": "gamepad", "keywords": ["gamepad", "controller", "game", "play", "gaming"]},
    {"name": "terminal", "keywords": ["terminal", "console", "command", "code", "cli"]},
    {"name": "chip", "keywords": ["chip", "cpu", "processor", "tech", "electronic"]},

    # Food & Drink
    {"name": "coffee", "keywords": ["coffee", "drink", "cafe", "morning", "caffeine", "cup"]},
    {"name": "beer", "keywords": ["beer", "drink", "alcohol", "pub", "bar", "party"]},
    {"name": "wine", "keywords": ["wine", "drink", "glass", "alcohol", "fancy"]},
    {"name": "pizza", "keywords": ["pizza", "food", "slice", "party", "snack"]},
    {"name": "apple", "keywords": ["apple", "fruit", "food", "healthy", "red"]},

    # Animals
    {"name": "cat", "keywords": ["cat", "pet", "animal", "kitty", "meow"]},
    {"name": "dog", "keywords": ["dog", "pet", "animal", "puppy", "woof"]},
    {"name": "bird", "keywords": ["bird", "animal", "fly", "tweet", "chirp"]},
    {"name": "fish", "keywords": ["fish", "animal", "water", "sea", "swim"]},
    {"name": "bug", "keywords": ["bug", "insect", "beetle", "creature"]},
    {"name": "spider", "keywords": ["spider", "web", "insect", "creepy", "halloween"]},
    {"name": "bat", "keywords": ["bat", "animal", "night", "vampire", "halloween", "fly"]},

    # Places & Buildings
    {"name": "home", "keywords": ["home", "house", "building", "residence", "place"]},
    {"name": "building", "keywords": ["building", "office", "city", "urban", "tower"]},
    {"name": "factory", "keywords": ["factory", "industrial", "manufacture", "production"]},
    {"name": "castle", "keywords": ["castle", "fortress", "medieval", "kingdom", "royal"]},
    {"name": "church", "keywords": ["church", "religion", "building", "worship"]},

    # Transport
    {"name": "car", "keywords": ["car", "vehicle", "drive", "auto", "transport"]},
    {"name": "plane", "keywords": ["plane", "airplane", "fly", "travel", "flight"]},
    {"name": "rocket", "keywords": ["rocket", "space", "launch", "blast", "fast"]},
    {"name": "ship", "keywords": ["ship", "boat", "sea", "sail", "ocean"]},
    {"name": "bicycle", "keywords": ["bicycle", "bike", "cycle", "ride", "pedal"]},

    # Gaming & RPG
    {"name": "sword", "keywords": ["sword", "weapon", "fight", "battle", "rpg", "warrior"]},
    {"name": "shield", "keywords": ["shield", "defense", "protect", "armor", "rpg"]},
    {"name": "axe", "keywords": ["axe", "weapon", "chop", "viking", "warrior"]},
    {"name": "bow", "keywords": ["bow", "arrow", "weapon", "archer", "hunt"]},
    {"name": "wand", "keywords": ["wand", "magic", "wizard", "spell", "fantasy"]},
    {"name": "potion", "keywords": ["potion", "magic", "drink", "elixir", "rpg", "health"]},
    {"name": "scroll", "keywords": ["scroll", "paper", "magic", "spell", "ancient"]},
    {"name": "chest", "keywords": ["chest", "treasure", "loot", "storage", "rpg", "gold"]},
    {"name": "dice", "keywords": ["dice", "game", "random", "chance", "roll", "tabletop"]},

    # Misc
    {"name": "lightbulb", "keywords": ["lightbulb", "idea", "bright", "think", "creative", "light"]},
    {"name": "wrench", "keywords": ["wrench", "tool", "fix", "repair", "settings"]},
    {"name": "gear", "keywords": ["gear", "settings", "cog", "configure", "options"]},
    {"name": "hammer", "keywords": ["hammer", "tool", "build", "construct", "work"]},
    {"name": "paint", "keywords": ["paint", "art", "brush", "color", "creative"]},
    {"name": "palette", "keywords": ["palette", "art", "color", "paint", "creative"]},
    {"name": "book", "keywords": ["book", "read", "library", "knowledge", "learn"]},
    {"name": "newspaper", "keywords": ["newspaper", "news", "article", "press", "media"]},
    {"name": "globe", "keywords": ["globe", "world", "earth", "international", "global"]},
    {"name": "map", "keywords": ["map", "location", "navigate", "travel", "direction"]},
    {"name": "pin", "keywords": ["pin", "location", "marker", "map", "place"]},
    {"name": "eye", "keywords": ["eye", "see", "view", "watch", "look", "vision"]},
    {"name": "hand", "keywords": ["hand", "point", "finger", "gesture", "touch"]},
    {"name": "thumbs-up", "keywords": ["thumbs", "up", "like", "good", "approve", "yes"]},
    {"name": "thumbs-down", "keywords": ["thumbs", "down", "dislike", "bad", "reject", "no"]},
    {"name": "peace", "keywords": ["peace", "victory", "two", "fingers", "sign"]},
    {"name": "fist", "keywords": ["fist", "punch", "power", "fight", "strong"]},
]

# Quick lookup by icon name
PIXEL_ICON_MAP = {icon["name"]: icon for icon in PIXEL_ICONS}

# All icon names for validation
PIXEL_ICON_NAMES = [icon["name"] for icon in PIXEL_ICONS]

# Default icon when none selected
DEFAULT_ICON = "folder"


def search_icons(query: str, limit: int = 50) -> list[dict]:
    """Search icons by name or keywords.

    Args:
        query: Search term (searches name and keywords)
        limit: Maximum number of results to return

    Returns:
        List of matching icon dictionaries
    """
    if not query:
        return PIXEL_ICONS[:limit]

    query = query.lower().strip()
    results = []

    for icon in PIXEL_ICONS:
        # Check if query matches name
        if query in icon["name"].lower():
            results.append(icon)
            continue

        # Check if query matches any keyword
        for keyword in icon["keywords"]:
            if query in keyword.lower():
                results.append(icon)
                break

    return results[:limit]


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
        True if the icon exists in the manifest
    """
    return icon_name in PIXEL_ICON_MAP
