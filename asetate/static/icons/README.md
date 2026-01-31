# Pixel Icons for Asetate

This directory contains 1,476 pixel icons used for crate icons throughout the application.

## Icon Source

**1-bit Pixel Icons by Nikoichu**
- License: CC0 (Public Domain)
- Download: https://nikoichu.itch.io/pixel-icons
- Icons: 1,400+ 16x16 pixel icons

## Categories

Icons are organized by category prefix:

| Category | Count | Examples |
|----------|-------|----------|
| Software | 176 | Folders, files, UI elements |
| Tools | 162 | Hammer, wrench, gear |
| RPG | 132 | Weapons, potions, items |
| Platforms | 127 | Brand logos, social media |
| Travel | 109 | Vehicles, landmarks |
| Boardgames | 108 | Cards, dice, tokens |
| Controller | 90 | Gamepad buttons |
| Map | 88 | Markers, flags, locations |
| Media | 84 | Play, pause, audio controls |
| Alchemy | 56 | Elements, zodiac, potions |
| Hats | 48 | Headwear styles |
| Sports | 44 | Balls, equipment |
| Food | 43 | Drinks, meals, snacks |
| Arrows | 43 | Directions, pointers |
| Misc | 40 | Various icons |
| Warfare | 38 | Weapons, military |
| Cosmetics | 34 | Beauty, makeup |
| Weather | 30 | Sun, rain, clouds |
| Emoji | 24 | Face expressions |

## Icon Naming Convention

Icons follow this naming pattern:
```
Category_Keyword1_Keyword2_..._KeywordN.png
```

Examples:
- `Alchemy_Element_Fire.png`
- `Software_File_Folder_Directory_Explorer.png`
- `RPG_Item_Weapon_Sword_Knight.png`

## Auto-Discovery

Icons are automatically discovered by scanning this directory. The filename is parsed to generate searchable keywords:

1. The filename (without `.png`) becomes the icon name
2. Each underscore-separated word becomes a keyword
3. Category synonyms are added automatically (e.g., "RPG" adds "game", "fantasy")
4. Common abbreviations are expanded (e.g., "UI" adds "interface")

No manual icon manifest is required - just add PNG files and they become searchable.

## Icon Format

- Size: 16x16 pixels (scaled up with `image-rendering: pixelated`)
- Format: PNG with transparency
- Color: Black pixels on transparent background (inverted via CSS)

## Adding Custom Icons

1. Create a 16x16 pixel PNG with black pixels on transparent background
2. Name it following the convention: `Category_Keywords.png`
3. Add it to this directory
4. The icon is automatically available in the picker

## Default Icon

The default icon (when none selected) is:
`Software_File_Folder_Directory_Explorer.png`

## License

The 1-bit Pixel Icons by Nikoichu are licensed under CC0 (Public Domain).
You can use them freely without attribution, though credit is appreciated.
