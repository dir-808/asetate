# Pixel Icons for Asetate

This directory contains pixel icons used for crate icons throughout the application.

## Required Icon Pack

**1-bit Pixel Icons by Nikoichu**
- License: CC0 (Public Domain)
- Download: https://nikoichu.itch.io/pixel-icons
- Icons: 1,400+ 16x16 pixel icons

## Installation

1. Download the icon pack from [itch.io](https://nikoichu.itch.io/pixel-icons)
2. Extract the downloaded archive
3. Navigate to the `Sprites` or `Sprites-Cropped` folder
4. Copy the PNG files you need into this directory (`asetate/static/icons/`)

### Required Icons

The application expects the following icon files (at minimum):

**Essential:**
- `folder.png` (default icon)
- `music.png`
- `heart.png`
- `star.png`
- `fire.png`

**Recommended (for full icon picker):**
See the icon manifest in `asetate/models/pixel_icons.py` for the complete list of expected icons.

## Icon Naming

Icons should be named in lowercase with hyphens for multi-word names:
- `music.png`
- `folder-open.png`
- `arrow-up.png`

## Icon Format

- Size: 16x16 pixels (will be scaled up with `image-rendering: pixelated`)
- Format: PNG with transparency
- Color: Black pixels on transparent background (icons are inverted via CSS)

## Adding Custom Icons

1. Create a 16x16 pixel PNG with black pixels on transparent background
2. Add the file to this directory
3. Add an entry to `PIXEL_ICONS` in `asetate/models/pixel_icons.py` with name and keywords

Example:
```python
{"name": "my-icon", "keywords": ["custom", "my", "icon"]},
```

## License

The 1-bit Pixel Icons by Nikoichu are licensed under CC0 (Public Domain).
You can use them freely without attribution, though credit is appreciated.
