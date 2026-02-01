# OpenMoji Emoji Icons

This directory contains OpenMoji outline-style emoji SVGs for crate icons.

## Source

**OpenMoji 16.0** - Open source emoji library
- Website: https://openmoji.org/
- License: CC BY-SA 4.0
- GitHub: https://github.com/hfg-gmuend/openmoji

## Setup

Run the setup script from the project root:

```bash
./scripts/download-emoji.sh
```

Or manually:

```bash
# Download the black/outline SVG pack
curl -L -o /tmp/openmoji-svg-black.zip \
  https://github.com/hfg-gmuend/openmoji/releases/download/16.0.0/openmoji-svg-black.zip

# Extract to this directory
unzip -o /tmp/openmoji-svg-black.zip -d asetate/static/emoji/

# Download the metadata JSON
curl -L -o asetate/static/emoji/openmoji.json \
  https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/data/openmoji.json

# Cleanup
rm /tmp/openmoji-svg-black.zip
```

## Contents

After setup:
- `*.svg` - ~3,600 outline emoji SVGs (named by Unicode hexcode)
- `openmoji.json` - Metadata with keywords, names, categories

## SVG Color Styling

These SVGs use `currentColor` for strokes, so they inherit text color:

```css
.emoji-icon {
    color: var(--crate-color, var(--text-primary));
}
```

## License

OpenMoji is licensed under CC BY-SA 4.0.
Attribution: OpenMoji (https://openmoji.org/)
